import hashlib
import math
import re
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from app.services.rag.models import DocumentChunk, RetrievalResult


class HybridDocumentRetriever:
    """Hybrid lexical and dense semantic document retriever with multilingual expansion.
    
    Combines:
    1. Lexical BM25 / TF-IDF scoring over official titles, clauses, and texts.
    2. Dense cosine vector similarity over normalized embedding representations.
    3. Multilingual civic vocabulary mapping (Kannada, Hindi, English).
    4. Thresholding to detect when retrieved evidence is insufficient for factual claims.
    """

    # Multilingual civic vocabulary mapping
    MULTILINGUAL_EXPANSIONS: Dict[str, List[str]] = {
        # Kannada terms
        "ಪಿಎಂ ಕಿಸಾನ್": ["pm-kisan", "pradhan mantri kisan samman nidhi", "farmer"],
        "ಕಿಸಾನ್": ["pm-kisan", "farmer", "agriculture"],
        "ಆದಾಯ": ["income", "annual family income", "income limit"],
        "ಆದಾಯ ಮಿತಿ": ["income cap", "income ceiling", "annual income"],
        "ಯಜಮಾನಿ": ["yajamani", "female head of family", "gruha lakshmi", "woman"],
        "ಗೃಹ ಲಕ್ಷ್ಮಿ": ["gruha lakshmi", "karnataka", "yajamani", "women"],
        "ವಿದ್ಯಾರ್ಥಿವೇತನ": ["scholarship", "post-matric", "csss", "ssp"],
        "ಜಮೀನು": ["landholding", "farmland", "cultivable land"],
        "ಭೂಮಿ": ["bhoomi", "land record", "farmland"],
        "ಇ-ದೃಢೀಕರಣ": ["e-attestation", "sop", "sakala"],
        "ಸಕಾಲ": ["sakala", "7 days", "statutory deadline"],
        "ಅರ್ಹತೆ": ["eligibility", "criteria", "requirements"],
        "ದಾಖಲೆ": ["document", "certificate", "ration card"],

        # Hindi terms
        "पीएम किसान": ["pm-kisan", "pradhan mantri kisan samman nidhi", "farmer"],
        "किसान": ["pm-kisan", "farmer", "agriculture"],
        "आय": ["income", "family income"],
        "आय सीमा": ["income cap", "income ceiling", "income limit"],
        "छात्रवृत्ति": ["scholarship", "nsp", "csss", "pragati"],
        "जमीन": ["landholding", "farmland", "cultivable land"],
        "भूमि": ["landholding", "farmland"],
        "गृह लक्ष्मी": ["gruha lakshmi", "female head"],
        "पात्रता": ["eligibility", "requirements", "criteria"],
        "दस्तावेज": ["document", "certificate"],
        "प्रमाण पत्र": ["certificate", "income certificate"],
        "अंतिम तिथि": ["deadline", "last date"],
        "आवेदन": ["application", "registration", "portal"],
    }

    def __init__(self, chunks: Optional[List[DocumentChunk]] = None, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.chunks: List[DocumentChunk] = []
        self.chunk_embeddings: Optional[np.ndarray] = None
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

        if chunks:
            self.index_chunks(chunks)

    def _tokenize(self, text: str) -> List[str]:
        """Simple, fast whitespace and punctuation tokenizer with lowercasing."""
        tokens = re.findall(r"\b[\w\.\-]+\b", text.lower())
        return [t for t in tokens if len(t) > 1]

    def _generate_dense_vector(self, text: str) -> np.ndarray:
        """Generates a stable, dense hash-projected unit embedding vector using NumPy.
        
        Guarantees deterministic, fast semantic representation without downloading gigabyte models.
        """
        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        tokens = self._tokenize(text)
        if not tokens:
            return vec

        for token in tokens:
            # Deterministic feature hashing
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.embedding_dim
            sign = 1.0 if (h >> 16) % 2 == 0 else -1.0
            vec[idx] += sign

        # Unit normalize (L2 norm)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def normalize_query(self, query: str) -> str:
        """Expands multilingual tokens (Kannada / Hindi) into target English civic terminology."""
        clean_query = query.strip()
        additions: List[str] = []

        for vernacular, equivalents in self.MULTILINGUAL_EXPANSIONS.items():
            if vernacular in clean_query:
                additions.extend(equivalents)

        if additions:
            clean_query = f"{clean_query} {' '.join(additions)}"
        return clean_query

    def index_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Indexes evidence chunks into lexical and dense vector structures."""
        self.chunks = chunks
        num_docs = len(chunks)
        if num_docs == 0:
            return

        # 1. Build Dense Matrix
        embeddings = []
        doc_frequencies: Dict[str, int] = {}

        for chunk in chunks:
            full_chunk_text = f"{chunk.document_title} {chunk.section_or_clause} {chunk.text}"
            vec = self._generate_dense_vector(full_chunk_text)
            embeddings.append(vec)

            # Lexical tracking
            unique_terms = set(self._tokenize(full_chunk_text))
            for term in unique_terms:
                doc_frequencies[term] = doc_frequencies.get(term, 0) + 1

        self.chunk_embeddings = np.array(embeddings, dtype=np.float32)

        # 2. Compute Lexical IDF
        self.idf = {
            term: math.log((num_docs + 1) / (df + 1)) + 1.0
            for term, df in doc_frequencies.items()
        }

    def _compute_lexical_score(self, query_tokens: List[str], chunk: DocumentChunk) -> float:
        """Computes BM25-inspired lexical score with title and clause weighting."""
        score = 0.0
        chunk_text_lower = chunk.text.lower()
        title_lower = chunk.document_title.lower()
        clause_lower = chunk.section_or_clause.lower()

        for term in query_tokens:
            term_idf = self.idf.get(term, 1.0)

            # Term frequency in main text
            count = chunk_text_lower.count(term)
            if count > 0:
                tf = count / (count + 1.2)
                score += tf * term_idf

            # High-value boosting for title and clause matches
            if term in title_lower:
                score += 1.5 * term_idf
            if term in clause_lower:
                score += 2.0 * term_idf

        return score

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        min_similarity: float = 0.22,
        scheme_filter: Optional[str] = None,
    ) -> RetrievalResult:
        """Retrieves most relevant official evidence chunks using hybrid reciprocal ranking."""
        normalized_q = self.normalize_query(query)
        q_tokens = self._tokenize(normalized_q)

        if not self.chunks or not q_tokens:
            return RetrievalResult(
                query=query,
                normalized_query=normalized_q,
                chunks=[],
                scores=[],
                sufficient_evidence=False,
            )

        # 1. Dense Cosine Similarity
        q_vec = self._generate_dense_vector(normalized_q)
        dense_scores = np.dot(self.chunk_embeddings, q_vec)  # (N,)

        # 2. Lexical Scores
        lexical_scores = np.array(
            [self._compute_lexical_score(q_tokens, c) for c in self.chunks],
            dtype=np.float32,
        )
        max_lex = np.max(lexical_scores) if len(lexical_scores) > 0 and np.max(lexical_scores) > 0 else 1.0
        normalized_lexical = lexical_scores / max_lex

        # 3. Hybrid Fusion Score (Dense + Lexical)
        hybrid_scores = 0.55 * dense_scores + 0.45 * normalized_lexical

        # Filter by scheme_id if requested
        valid_indices = list(range(len(self.chunks)))
        if scheme_filter:
            valid_indices = [
                i for i in valid_indices if self.chunks[i].scheme_id == scheme_filter
            ]

        if not valid_indices:
            return RetrievalResult(
                query=query,
                normalized_query=normalized_q,
                chunks=[],
                scores=[],
                sufficient_evidence=False,
            )

        # Sort indices by score descending
        sorted_indices = sorted(valid_indices, key=lambda i: float(hybrid_scores[i]), reverse=True)
        top_indices = sorted_indices[:top_k]

        retrieved_chunks = [self.chunks[i] for i in top_indices]
        retrieved_scores = [round(float(hybrid_scores[i]), 4) for i in top_indices]

        # Check sufficiency threshold
        highest_score = retrieved_scores[0] if retrieved_scores else 0.0
        sufficient = highest_score >= min_similarity

        return RetrievalResult(
            query=query,
            normalized_query=normalized_q,
            chunks=retrieved_chunks,
            scores=retrieved_scores,
            sufficient_evidence=sufficient,
        )

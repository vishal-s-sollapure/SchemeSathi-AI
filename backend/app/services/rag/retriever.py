import hashlib
import math
import re
from typing import Dict, List, Optional, Set, Tuple

from app.services.rag.models import DocumentChunk, RetrievalResult


class HybridDocumentRetriever:
    """Pure-Python hybrid lexical and dense semantic document retriever with multilingual expansion.
    
    Guarantees:
    - Zero native C-extension / DLL dependencies (completely immune to Windows AppLocker DLL blocks).
    - Dense cosine vector similarity over deterministic hash-projected unit embedding vectors.
    - BM25-inspired lexical scoring with title and clause priority boosting.
    - Multilingual civic vocabulary mapping (Kannada, Hindi, English).
    - Strict thresholding detecting when evidence is insufficient for factual claims.
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
        "ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು": ["pm-kisan", "gruha lakshmi", "csss", "pragati", "ssp", "scholarship", "scheme", "eligibility"],
        "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು": ["pm-kisan", "gruha lakshmi", "csss", "pragati", "ssp", "scholarship", "scheme"],
        "ಯೋಜನೆಗಳು": ["scheme", "pm-kisan", "gruha lakshmi", "csss", "pragati", "scholarship"],
        "ಸಿಗಬಹುದು": ["qualify", "eligibility", "eligible", "benefit"],

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
        "सरकारी योजनाएं": ["pm-kisan", "gruha lakshmi", "csss", "pragati", "ssp", "scholarship", "scheme"],
        "योजनाएं": ["scheme", "pm-kisan", "gruha lakshmi", "csss", "pragati", "scholarship"],
        "मिल सकती हैं": ["qualify", "eligibility", "benefit", "scheme"],
    }

    # Stopwords to prevent generic function words from overpowering semantic intent
    STOPWORDS: Set[str] = {
        "the", "a", "an", "is", "are", "was", "were", "to", "in", "for", "of", "and",
        "or", "on", "at", "by", "from", "with", "about", "what", "how", "who", "which",
        "when", "where", "can", "do", "does", "did", "under", "all", "get", "claim",
        "this", "that", "these", "those", "have", "has", "had", "receive", "support",
        "applicable", "eligible", "scheme", "policy", "financial",
    }

    # Distinctive scheme aliases for targeted intent boosting
    SCHEME_TARGETS: Dict[str, List[str]] = {
        "SCHEME-PM-KISAN": ["pm-kisan", "pmkisan", "kisan", "samman", "farmer"],
        "POL-PMKISAN-EKYC-EXCLUSION": ["pm-kisan", "pmkisan", "kisan", "samman", "farmer"],
        "SCH-MOE-CSSS-2024": ["csss", "pm-usp", "central sector", "percentile"],
        "SCH-KAR-SSP-SC-2024": ["ssp", "post-matric", "scheduled caste"],
        "SCH-AICTE-PRAGATI-DEGREE": ["pragati", "aicte", "girl student", "daughters"],
        "SCHEME-KAR-GRUHA-LAKSHMI": ["gruha", "lakshmi", "yajamani", "female head"],
        "POL-SSP-EATTEST-CIRCULAR": ["sakala", "e-attestation", "eattest", "attestation", "7 days"],
        "POL-NSP-OTR-GUIDELINE": ["otr", "one-time registration", "facerd"],
    }

    def __init__(self, chunks: Optional[List[DocumentChunk]] = None, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.chunks: List[DocumentChunk] = []
        self.chunk_embeddings: List[List[float]] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

        if chunks:
            self.index_chunks(chunks)

    def _tokenize(self, text: str) -> List[str]:
        """Simple, fast whitespace and punctuation tokenizer with lowercasing."""
        tokens = re.findall(r"\b[\w\.\-]+\b", text.lower())
        return [t for t in tokens if len(t) > 1]

    def _generate_dense_vector(self, text: str) -> List[float]:
        """Generates a stable, dense hash-projected unit embedding vector in pure Python.
        
        Guarantees deterministic semantic representation without external model downloads or native DLLs.
        """
        vec = [0.0] * self.embedding_dim
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
        norm_sq = sum(x * x for x in vec)
        if norm_sq > 0:
            norm = math.sqrt(norm_sq)
            vec = [x / norm for x in vec]
        return vec

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Pure-Python dot product of unit-normalized vectors."""
        return sum(a * b for a, b in zip(v1, v2))

    def normalize_query(self, query: str) -> str:
        """Expands multilingual tokens (Kannada / Hindi) into target English civic terminology."""
        clean_query = query.strip()
        additions: List[str] = []

        for vernacular, equivalents in self.MULTILINGUAL_EXPANSIONS.items():
            if vernacular in clean_query:
                additions.extend(equivalents)

        low = clean_query.lower()
        if any(p in low for p in ["what government schemes", "which government schemes", "what schemes", "may i qualify", "qualify for"]):
            additions.extend(["pm-kisan", "gruha lakshmi", "csss", "pragati", "ssp", "scholarship", "eligibility"])

        if additions:
            clean_query = f"{clean_query} {' '.join(additions)}"
        return clean_query

    def index_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Indexes evidence chunks into lexical and dense vector structures."""
        self.chunks = chunks
        num_docs = len(chunks)
        if num_docs == 0:
            return

        # 1. Build Dense Embedding List
        embeddings: List[List[float]] = []
        doc_frequencies: Dict[str, int] = {}

        for chunk in chunks:
            full_chunk_text = f"{chunk.document_title} {chunk.section_or_clause} {chunk.text}"
            vec = self._generate_dense_vector(full_chunk_text)
            embeddings.append(vec)

            # Lexical tracking
            unique_terms = set(self._tokenize(full_chunk_text))
            for term in unique_terms:
                doc_frequencies[term] = doc_frequencies.get(term, 0) + 1

        self.chunk_embeddings = embeddings

        # 2. Compute Lexical IDF
        self.idf = {
            term: math.log((num_docs + 1) / (df + 1)) + 1.0
            for term, df in doc_frequencies.items()
        }

    def _get_scheme_intent_boost(self, normalized_q: str, chunk: DocumentChunk) -> float:
        """Provides strong intent boosting when recognized civic scheme aliases appear in query."""
        boost = 0.0
        q_lower = normalized_q.lower()
        chunk_title = chunk.document_title.lower()
        chunk_clause = chunk.section_or_clause.lower()
        chunk_scheme = (chunk.scheme_id or "").upper()

        for scheme_key, aliases in self.SCHEME_TARGETS.items():
            matched_aliases = [alias for alias in aliases if alias in q_lower]
            if matched_aliases:
                # Direct scheme ID association
                if chunk_scheme == scheme_key or (scheme_key.replace("SCHEME-", "").replace("POL-", "") in chunk_scheme):
                    boost += 14.0
                # Content / title association
                for alias in matched_aliases:
                    if alias in chunk_title:
                        boost += 6.0
                    if alias in chunk_clause:
                        boost += 4.0

        return boost

    def _compute_lexical_score(self, query_tokens: List[str], chunk: DocumentChunk, normalized_q: str) -> float:
        """Computes BM25-inspired lexical score with title, clause, and intent weighting."""
        score = 0.0
        chunk_text_lower = chunk.text.lower()
        title_lower = chunk.document_title.lower()
        clause_lower = chunk.section_or_clause.lower()

        # Scheme intent boost
        score += self._get_scheme_intent_boost(normalized_q, chunk)

        meaningful_tokens = [t for t in query_tokens if t not in self.STOPWORDS and len(t) > 1]

        for term in meaningful_tokens:
            term_idf = self.idf.get(term, 1.0)

            # Term frequency in main text
            count = chunk_text_lower.count(term)
            if count > 0:
                tf = count / (count + 1.2)
                score += tf * term_idf * 2.0

            # High-value boosting for title and clause matches
            if term in title_lower:
                score += 3.0 * term_idf
            if term in clause_lower:
                score += 4.0 * term_idf

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

        meaningful_tokens = [t for t in q_tokens if t not in self.STOPWORDS and len(t) > 2]

        # 1. Dense Cosine Similarities (Pure Python)
        q_vec = self._generate_dense_vector(normalized_q)
        dense_scores = [self._cosine_similarity(chunk_vec, q_vec) for chunk_vec in self.chunk_embeddings]

        # 2. Lexical Scores
        lexical_scores = [
            self._compute_lexical_score(q_tokens, c, normalized_q) for c in self.chunks
        ]

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

        # 3. Hybrid Fusion Score (Dominant Lexical Precision + Dense Semantic Context)
        hybrid_scores = [
            (lexical_scores[i] * 0.7) + (max(dense_scores[i], 0.0) * 10.0 * 0.3)
            for i in range(len(self.chunks))
        ]

        # Sort indices by score descending
        sorted_indices = sorted(valid_indices, key=lambda i: hybrid_scores[i], reverse=True)
        top_indices = sorted_indices[:top_k]

        top_idx = top_indices[0] if top_indices else -1
        highest_lex = lexical_scores[top_idx] if top_idx >= 0 else 0.0

        # Check sufficiency: Grounded civic claims must match meaningful query terms
        if top_idx >= 0 and meaningful_tokens:
            top_chunk = self.chunks[top_idx]
            top_chunk_all_text = f"{top_chunk.document_title} {top_chunk.section_or_clause} {top_chunk.text}".lower()
            matched_terms = [t for t in meaningful_tokens if t in top_chunk_all_text]
            has_scheme_target = any(
                alias in normalized_q.lower() and (alias in top_chunk_all_text or top_chunk.scheme_id == skey)
                for skey, aliases in self.SCHEME_TARGETS.items()
                for alias in aliases
            )
            # Evidence is sufficient if:
            # - At least 2 meaningful terms matched with strong lexical signal, OR
            # - A recognized scheme target matched with at least 1 term, OR
            # - For 1-word queries, that exact term matched
            sufficient = (
                (len(matched_terms) >= 2 and highest_lex >= 2.0)
                or (has_scheme_target and len(matched_terms) >= 1 and highest_lex >= 2.0)
                or (len(meaningful_tokens) == 1 and len(matched_terms) == 1 and highest_lex >= 1.5)
            )
        else:
            sufficient = False

        retrieved_chunks = [self.chunks[i] for i in top_indices] if sufficient else []
        retrieved_scores = [round(hybrid_scores[i], 4) for i in top_indices] if sufficient else []

        return RetrievalResult(
            query=query,
            normalized_query=normalized_q,
            chunks=retrieved_chunks,
            scores=retrieved_scores,
            sufficient_evidence=sufficient,
        )

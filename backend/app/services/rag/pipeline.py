import logging
from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.services.rag.citation_validator import CitationValidator
from app.services.rag.generator import GroundedResponseGenerator
from app.services.rag.ingestion import OfficialDocumentIngestion
from app.services.rag.models import DocumentChunk, RAGResponse
from app.services.rag.retriever import HybridDocumentRetriever
from app.services.rag.security import PromptInjectionGuard

logger = logging.getLogger("rag_pipeline")


class RAGPipeline:
    """End-to-end Retrieval-Augmented Generation & Official Citation Engine.
    
    Orchestrates:
    - Official Knowledge Base Ingestion
    - Hierarchical Section-Aware Chunking
    - Untrusted Input Sanitization & Security Boundary Isolation
    - Hybrid Lexical & Dense Vector Retrieval with Multilingual Expansion
    - Grounded Response Generation in English, Kannada, and Hindi
    - Strict Post-Generation Citation Validation
    """

    _instance: Optional["RAGPipeline"] = None

    def __init__(self, seeds_dir: Optional[Path] = None):
        self.ingestion = OfficialDocumentIngestion()
        self.retriever = HybridDocumentRetriever(embedding_dim=settings.EMBEDDING_DIM)
        self.is_initialized = False

        if seeds_dir:
            self.initialize(seeds_dir)

    @classmethod
    def get_instance(cls, seeds_dir: Optional[Path] = None) -> "RAGPipeline":
        """Singleton accessor for the global RAG pipeline."""
        if cls._instance is None:
            default_seeds = Path(__file__).resolve().parent.parent.parent / "data" / "seeds"
            target_dir = seeds_dir or default_seeds
            cls._instance = RAGPipeline(target_dir)
        return cls._instance

    def initialize(self, seeds_dir: Path) -> int:
        """Loads and indexes official knowledge base seeds into the hybrid retriever."""
        if not seeds_dir.exists():
            logger.error(f"Seeds directory not found at {seeds_dir}")
            return 0

        chunks = self.ingestion.build_initial_knowledge_base(seeds_dir)
        self.retriever.index_chunks(chunks)
        self.is_initialized = True
        logger.info(f"RAG Pipeline successfully initialized with {len(chunks)} verified evidence chunks.")
        return len(chunks)

    def ingest_pdf(
        self,
        pdf_path: Path,
        document_title: str,
        government_department: str,
        official_source_url: str,
        scheme_id: Optional[str] = None,
        applicable_cycle: str = "2024-25",
    ) -> int:
        """Ingests an official PDF file into the live retriever index."""
        new_chunks = self.ingestion.ingest_pdf_document(
            pdf_path=pdf_path,
            document_title=document_title,
            government_department=government_department,
            official_source_url=official_source_url,
            scheme_id=scheme_id,
            applicable_cycle=applicable_cycle,
        )
        if new_chunks:
            all_chunks = self.retriever.chunks + new_chunks
            self.retriever.index_chunks(all_chunks)
            logger.info(f"Added {len(new_chunks)} chunks from PDF: {pdf_path.name}")
        return len(new_chunks)

    def ask(
        self,
        query: str,
        language: Optional[str] = None,
        scheme_filter: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> RAGResponse:
        """Processes a citizen inquiry through the end-to-end grounded RAG pipeline."""
        # 1. Security Check: Validate user query for adversarial prompt injections
        is_safe, security_reason = PromptInjectionGuard.is_safe_query(query)
        if not is_safe:
            logger.warning(f"Blocked unsafe query: '{query[:60]}...' Reason: {security_reason}")
            lang = language or GroundedResponseGenerator.detect_language(query)
            return RAGResponse(
                query=query,
                answer=(
                    "Security Notice: Your query contains instructions that attempt to override "
                    "system safety boundaries or prompt execution rules. SchemeSathi AI processes "
                    "only factual civic inquiries regarding government schemes and policies."
                ),
                language=lang,
                citations=[],
                confidence_score=0.0,
                is_grounded=True,
                sufficient_evidence=False,
                suggested_follow_ups=[
                    "What are the eligibility criteria for PM-KISAN?",
                    "What is the parental income ceiling for CSSS scholarships?",
                ],
            )

        # 2. Hybrid Document Retrieval (Lexical + Dense Semantic + Multilingual Expansion)
        k = top_k or settings.RAG_TOP_K
        retrieval = self.retriever.retrieve(
            query=query,
            top_k=k,
            min_similarity=settings.RAG_MIN_SIMILARITY,
            scheme_filter=scheme_filter,
        )

        # 3. Grounded Response Generation
        response = GroundedResponseGenerator.generate_response(
            query=query,
            retrieved_chunks=retrieval.chunks,
            sufficient_evidence=retrieval.sufficient_evidence,
            language_override=language,
        )

        # 4. Strict Post-Generation Citation Validation
        # Verify candidate citations against retrieved chunks to ensure zero hallucinations
        validated_citations = CitationValidator.validate_citations(
            candidate_citations=[c.model_dump() for c in response.citations],
            retrieved_chunks=retrieval.chunks,
        )
        response.citations = validated_citations

        return response

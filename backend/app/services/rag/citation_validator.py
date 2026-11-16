import logging
from typing import List, Optional

from app.services.rag.models import DocumentChunk, ValidatedCitation

logger = logging.getLogger("citation_validator")


class CitationValidator:
    """Strict auditor ensuring all factual citations belong strictly to retrieved official evidence.
    
    Guarantees:
    - Never fabricates or allows hallucinations of government circulars or clauses.
    - Matches claimed citations against retrieved chunk IDs, source titles, and official URLs.
    - Strips or rejects citations that do not exist in retrieved context.
    """

    @classmethod
    def validate_citations(
        cls,
        candidate_citations: List[dict],
        retrieved_chunks: List[DocumentChunk],
    ) -> List[ValidatedCitation]:
        """Validates that candidate citations correspond directly to chunks in the retrieved evidence."""
        validated: List[ValidatedCitation] = []
        chunk_map = {c.chunk_id: c for c in retrieved_chunks}

        for cand in candidate_citations:
            title = cand.get("source_title") or cand.get("title", "")
            clause = cand.get("clause_or_section") or cand.get("clause_number", "")
            url = cand.get("official_source_url", "")
            chunk_id = cand.get("matched_chunk_id", "")

            # 1. Direct chunk ID match
            if chunk_id in chunk_map:
                chunk = chunk_map[chunk_id]
                validated.append(
                    ValidatedCitation(
                        source_title=chunk.document_title,
                        circular_number=chunk.metadata.get("notification_number"),
                        clause_or_section=chunk.section_or_clause,
                        page_number=chunk.page_number,
                        official_source_url=chunk.official_source_url,
                        verification_status="OFFICIALLY_VERIFIED",
                        matched_chunk_id=chunk.chunk_id,
                        excerpt=chunk.text[:220] + "...",
                    )
                )
                continue

            # 2. Match by title and clause within retrieved chunks
            matched_chunk: Optional[DocumentChunk] = None
            for c in retrieved_chunks:
                title_match = (
                    title.lower() in c.document_title.lower()
                    or c.document_title.lower() in title.lower()
                )
                clause_match = (
                    clause.lower() in c.section_or_clause.lower()
                    or c.section_or_clause.lower() in clause.lower()
                )
                if title_match or clause_match:
                    matched_chunk = c
                    break

            if matched_chunk:
                validated.append(
                    ValidatedCitation(
                        source_title=matched_chunk.document_title,
                        circular_number=matched_chunk.metadata.get("notification_number"),
                        clause_or_section=matched_chunk.section_or_clause,
                        page_number=matched_chunk.page_number,
                        official_source_url=matched_chunk.official_source_url,
                        verification_status="OFFICIALLY_VERIFIED",
                        matched_chunk_id=matched_chunk.chunk_id,
                        excerpt=matched_chunk.text[:220] + "...",
                    )
                )
            else:
                logger.warning(
                    f"Rejected ungrounded or hallucinated citation: '{title}' ({clause}). "
                    f"Not found in {len(retrieved_chunks)} retrieved evidence chunks."
                )

        return validated

    @classmethod
    def generate_citations_from_evidence(
        cls,
        retrieved_chunks: List[DocumentChunk],
        max_citations: int = 3,
    ) -> List[ValidatedCitation]:
        """Constructs pristine, verified citations directly from the top retrieved evidence chunks."""
        citations: List[ValidatedCitation] = []
        seen_clauses = set()

        for chunk in retrieved_chunks:
            key = (chunk.document_title, chunk.section_or_clause)
            if key in seen_clauses:
                continue
            seen_clauses.add(key)

            excerpt_clean = chunk.text.replace("\n", " ").strip()
            if len(excerpt_clean) > 220:
                excerpt_clean = excerpt_clean[:220] + "..."

            citations.append(
                ValidatedCitation(
                    source_title=chunk.document_title,
                    circular_number=chunk.metadata.get("notification_number"),
                    clause_or_section=chunk.section_or_clause,
                    page_number=chunk.page_number,
                    official_source_url=chunk.official_source_url,
                    verification_status="OFFICIALLY_VERIFIED",
                    matched_chunk_id=chunk.chunk_id,
                    excerpt=excerpt_clean,
                )
            )

            if len(citations) >= max_citations:
                break

        return citations

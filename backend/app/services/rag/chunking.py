import re
from typing import Any, Dict, List, Optional
import unicodedata

from app.services.rag.models import DocumentChunk
from app.services.rag.security import PromptInjectionGuard


class SectionAwareChunker:
    """Hierarchical, section-aware chunker designed for official Indian government circulars and guidelines.
    
    Preserves clause numbers, statutory conditions, and legislative context without arbitrary cutting.
    """

    CLAUSE_PATTERN = re.compile(
        r"(?:^|\n)(?P<heading>(?:Clause|Section|Para|Paragraph|Rule|Article)\s+[\d\.\(\)a-zA-Z]+[^\n]*|\d+\.\d+\s+[^\n]+)",
        re.IGNORECASE,
    )

    def __init__(self, max_chunk_size: int = 700, min_chunk_size: int = 150, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap = overlap

    def clean_text(self, text: str) -> str:
        """Cleans government text, resolving OCR artifacts, broken hyphens and erratic whitespaces."""
        if not text:
            return ""

        # Normalize unicode
        text = unicodedata.normalize("NFKC", text)

        # Fix hyphenated words across line breaks (e.g. "scholar-\nship" -> "scholarship")
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

        # Normalize carriage returns and tabs
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")

        # Collapse excessive spaces and blank lines
        text = re.sub(r"[ ]{2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return PromptInjectionGuard.sanitize_untrusted_text(text)

    def chunk_section(
        self,
        text: str,
        document_title: str,
        section_or_clause: str,
        official_source_url: str,
        government_department: str,
        page_number: Optional[str] = None,
        scheme_id: Optional[str] = None,
        applicable_cycle: str = "2024-25 / 2025-26",
        base_chunk_id: str = "CHK",
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """Chunks a coherent legal section/clause, breaking down further only when size ceiling is breached."""
        clean_section = self.clean_text(text)
        if not clean_section:
            return []

        chunks: List[DocumentChunk] = []
        extra = extra_metadata or {}

        # If section is small enough, keep as single atomic chunk
        if len(clean_section) <= self.max_chunk_size:
            chunk_id = f"{base_chunk_id}-1"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=clean_section,
                    document_title=document_title,
                    scheme_id=scheme_id,
                    official_source_url=official_source_url,
                    government_department=government_department,
                    page_number=str(page_number) if page_number else None,
                    section_or_clause=section_or_clause,
                    applicable_cycle=applicable_cycle,
                    verification_status="VERIFIED",
                    metadata=extra,
                )
            )
            return chunks

        # Otherwise, split by sentences/paragraphs with overlap
        sentences = re.split(r"(?<=[.!?])\s+", clean_section)
        current_text = ""
        part_idx = 1

        for sentence in sentences:
            if len(current_text) + len(sentence) + 1 <= self.max_chunk_size:
                current_text = f"{current_text} {sentence}".strip()
            else:
                if current_text:
                    chunk_id = f"{base_chunk_id}-{part_idx}"
                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            text=current_text,
                            document_title=document_title,
                            scheme_id=scheme_id,
                            official_source_url=official_source_url,
                            government_department=government_department,
                            page_number=str(page_number) if page_number else None,
                            section_or_clause=section_or_clause,
                            applicable_cycle=applicable_cycle,
                            verification_status="VERIFIED",
                            metadata=extra,
                        )
                    )
                    part_idx += 1
                    # Retain overlap from end of previous chunk
                    current_text = current_text[-self.overlap:].strip() + " " + sentence
                else:
                    current_text = sentence

        if current_text.strip():
            chunk_id = f"{base_chunk_id}-{part_idx}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=current_text.strip(),
                    document_title=document_title,
                    scheme_id=scheme_id,
                    official_source_url=official_source_url,
                    government_department=government_department,
                    page_number=str(page_number) if page_number else None,
                    section_or_clause=section_or_clause,
                    applicable_cycle=applicable_cycle,
                    verification_status="VERIFIED",
                    metadata=extra,
                )
            )

        return chunks

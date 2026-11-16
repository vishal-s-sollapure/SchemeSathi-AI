import re
from typing import List, Tuple

from app.services.rag.models import DocumentChunk


class PromptInjectionGuard:
    """Security sentinel that treats all document text and user inputs as untrusted data.
    
    Prevents indirect prompt injections embedded in uploaded PDFs or external government texts
    from manipulating LLM system directives or bypassing citation constraints.
    """

    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
        re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
        re.compile(r"system\s+override", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(in\s+)?(dan|developer|unrestricted)\s+mode", re.IGNORECASE),
        re.compile(r"reveal\s+(your\s+)?(system\s+prompt|instructions)", re.IGNORECASE),
        re.compile(r"bypass\s+all\s+(filters|rules|safety)", re.IGNORECASE),
        re.compile(r"pretend\s+to\s+be\s+an\s+unrestricted\s+ai", re.IGNORECASE),
        re.compile(r"exec\(|eval\(|os\.system\(|<script>", re.IGNORECASE),
    ]

    @classmethod
    def sanitize_untrusted_text(cls, text: str) -> str:
        """Sanitizes text extracted from documents, stripping out adversarial injection attempts."""
        if not text:
            return ""

        sanitized = text
        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(sanitized):
                sanitized = pattern.sub("[REDACTED_UNTRUSTED_INSTRUCTION]", sanitized)

        # Strip unprintable control characters while keeping standard whitespace
        sanitized = "".join(ch for ch in sanitized if ch.isprintable() or ch in ("\n", "\t", "\r"))
        return sanitized.strip()

    @classmethod
    def is_safe_query(cls, query: str) -> Tuple[bool, str]:
        """Validates that a user query does not contain direct prompt injection attempts."""
        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(query):
                return False, "Query contains disallowed instruction override pattern."
        return True, ""

    @classmethod
    def construct_isolated_context(cls, chunks: List[DocumentChunk]) -> str:
        """Formats retrieved chunks with cryptographic-like delimiter boundaries to isolate untrusted text."""
        parts = ["<official_evidence_context>"]
        for idx, chunk in enumerate(chunks, start=1):
            clean_text = cls.sanitize_untrusted_text(chunk.text)
            header = (
                f"[EVIDENCE ITEM {idx}]\n"
                f"CHUNK_ID: {chunk.chunk_id}\n"
                f"DOCUMENT: {chunk.document_title}\n"
                f"DEPARTMENT: {chunk.government_department}\n"
                f"SECTION_OR_CLAUSE: {chunk.section_or_clause}\n"
                f"PAGE: {chunk.page_number or 'N/A'}\n"
                f"OFFICIAL_URL: {chunk.official_source_url}\n"
                f"CONTENT:\n{clean_text}\n"
            )
            parts.append(header)
        parts.append("</official_evidence_context>")
        return "\n".join(parts)

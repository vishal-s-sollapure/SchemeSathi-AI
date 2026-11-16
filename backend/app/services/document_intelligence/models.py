from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExtractedFieldCandidate(BaseModel):
    """A candidate field extracted from document text with confidence score and page location."""
    field_key: str  # student_name, course, marks_percentage, annual_income, etc.
    evidence_type: str  # BENEFICIARY_NAME, COURSE, MARKS_CARD, ANNUAL_INCOME, etc.
    extracted_value: str
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
    page_number: int = Field(1, ge=1)
    raw_text_snippet: str
    bounding_box: Optional[List[float]] = None


class ProcessedDocumentResult(BaseModel):
    """Result of parsing and analyzing a document file."""
    original_filename: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    page_count: int
    pages_text: List[Dict[str, Any]] = []
    ocr_applied: bool = False
    detected_document_type: str = "GENERAL_DOCUMENT"
    candidates: List[ExtractedFieldCandidate] = []
    disclaimer: str = (
        "Extracted for data entry assistance only; text extraction does not verify document authenticity. "
        "Official validation requires departmental database cross-matching via RD number or e-KYC."
    )

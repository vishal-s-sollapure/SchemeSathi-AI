from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExtractedEvidenceBase(BaseModel):
    evidence_type: str = Field(..., max_length=100)  # CERT_NUMBER, ISSUE_DATE, BENEFICIARY_NAME, ANNUAL_INCOME, CASTE_CATEGORY, COURSE, INSTITUTION, MARKS
    field_key: Optional[str] = Field(None, max_length=100)  # student_name, course, marks_percentage, annual_income, etc.
    extracted_value: str = Field(..., max_length=500)
    confirmed_value: Optional[str] = Field(None, max_length=500)
    is_confirmed: bool = Field(False)
    confirmed_at: Optional[datetime] = None
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
    page_number: Optional[int] = None
    bounding_box: Optional[List[float]] = None
    raw_text_snippet: Optional[str] = None
    official_source_id: Optional[str] = None
    verification_disclaimer: str = Field(
        "Extracted for data entry assistance only; text extraction does not verify document authenticity. Official validation requires departmental database cross-matching."
    )


class ExtractedEvidenceCreate(ExtractedEvidenceBase):
    id: Optional[str] = None
    document_id: str


class ExtractedEvidenceResponse(ExtractedEvidenceBase):
    id: str
    document_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UploadedDocumentBase(BaseModel):
    document_type: str = Field(..., max_length=100)
    original_filename: str = Field(..., max_length=255)
    file_size_bytes: int = Field(..., ge=0)
    mime_type: str = Field(..., max_length=100)
    sha256_hash: str = Field(..., max_length=64)
    page_count: int = Field(1, ge=1)
    ocr_applied: bool = Field(False)
    extra_metadata: Optional[Dict[str, Any]] = None


class UploadedDocumentCreate(UploadedDocumentBase):
    id: Optional[str] = None
    user_id: Optional[str] = None
    student_profile_id: Optional[str] = None
    citizen_profile_id: Optional[str] = None
    storage_path: str


class UploadedDocumentResponse(UploadedDocumentBase):
    id: str
    user_id: Optional[str] = None
    student_profile_id: Optional[str] = None
    citizen_profile_id: Optional[str] = None
    storage_path: str
    processing_status: str
    created_at: datetime
    updated_at: datetime
    extracted_evidence: List[ExtractedEvidenceResponse] = []

    model_config = ConfigDict(from_attributes=True)


class EvidenceConfirmationItem(BaseModel):
    evidence_id: str
    confirmed_value: str
    is_confirmed: bool = True


class EvidenceConfirmationRequest(BaseModel):
    items: List[EvidenceConfirmationItem]


class DocumentIntelligenceResponse(BaseModel):
    document: UploadedDocumentResponse
    extracted_candidates: List[ExtractedEvidenceResponse]
    page_count: int
    ocr_applied: bool
    detected_document_type: str
    disclaimer: str


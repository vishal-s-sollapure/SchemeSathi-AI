from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExtractedEvidenceBase(BaseModel):
    evidence_type: str = Field(..., max_length=100)  # CERT_NUMBER, ISSUE_DATE, BENEFICIARY_NAME, ANNUAL_INCOME, CASTE_CATEGORY
    extracted_value: str = Field(..., max_length=500)
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
    page_number: Optional[int] = None
    bounding_box: Optional[List[float]] = None
    raw_text_snippet: Optional[str] = None
    official_source_id: Optional[str] = None


class ExtractedEvidenceCreate(ExtractedEvidenceBase):
    id: Optional[str] = None
    document_id: str


class ExtractedEvidenceResponse(ExtractedEvidenceBase):
    id: str
    document_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UploadedDocumentBase(BaseModel):
    document_type: str = Field(..., max_length=100)
    original_filename: str = Field(..., max_length=255)
    file_size_bytes: int = Field(..., ge=0)
    mime_type: str = Field(..., max_length=100)
    sha256_hash: str = Field(..., max_length=64)


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

    class Config:
        from_attributes = True

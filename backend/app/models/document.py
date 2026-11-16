from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class UploadedDocument(Base, TimestampMixin):
    """User-uploaded document record for processing and verification readiness."""
    __tablename__ = "uploaded_documents"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    citizen_profile_id = Column(String(36), ForeignKey("citizen_profiles.id", ondelete="SET NULL"), nullable=True, index=True)

    document_type = Column(String(100), nullable=False, index=True)  # INCOME_CERT, CASTE_CERT, BONAFIDE, PASSBOOK, etc.
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    processing_status = Column(String(50), default="PENDING", nullable=False)  # PENDING, PROCESSED, FAILED
    page_count = Column(Integer, default=1, nullable=False)
    ocr_applied = Column(Boolean, default=False, nullable=False)
    extra_metadata = Column(JSON, default=dict, nullable=True)

    # Relationships
    user = relationship("User", back_populates="uploaded_documents")
    student_profile = relationship("StudentProfile", back_populates="uploaded_documents")
    citizen_profile = relationship("CitizenProfile", back_populates="uploaded_documents")
    extracted_evidence = relationship("ExtractedEvidence", back_populates="uploaded_document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UploadedDocument {self.id}: {self.original_filename} ({self.processing_status})>"


class ExtractedEvidence(Base, TimestampMixin):
    """Structured evidence extracted from uploaded documents or verified gazettes."""
    __tablename__ = "extracted_evidence"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    document_id = Column(String(50), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    official_source_id = Column(String(50), ForeignKey("official_sources.id", ondelete="SET NULL"), nullable=True)

    evidence_type = Column(String(100), nullable=False, index=True)  # CERT_NUMBER, ISSUE_DATE, BENEFICIARY_NAME, ANNUAL_INCOME, CASTE_CATEGORY
    field_key = Column(String(100), nullable=True, index=True)  # student_name, course, marks_percentage, annual_income, etc.
    extracted_value = Column(String(500), nullable=False)
    confirmed_value = Column(String(500), nullable=True)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    confidence_score = Column(Float, default=1.0, nullable=False)
    page_number = Column(Integer, nullable=True)
    bounding_box = Column(JSON, nullable=True)  # coordinates [x0, y0, x1, y1]
    raw_text_snippet = Column(Text, nullable=True)
    verification_disclaimer = Column(
        String(500),
        default="Extracted for data entry assistance only; text extraction does not verify document authenticity. Official validation requires departmental database cross-matching.",
        nullable=False,
    )

    # Relationships
    uploaded_document = relationship("UploadedDocument", back_populates="extracted_evidence")
    official_source = relationship("OfficialSource", back_populates="extracted_evidence")

    def __repr__(self) -> str:
        return f"<ExtractedEvidence {self.id}: {self.evidence_type} = '{self.extracted_value}' (confirmed={self.is_confirmed})>"

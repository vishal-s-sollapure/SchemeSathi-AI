from sqlalchemy import Column, Date, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class OfficialSource(Base, TimestampMixin):
    """Verified official government source reference (Gazette, Circular, Official Order)."""
    __tablename__ = "official_sources"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    source_title = Column(String(255), nullable=False)
    issuing_authority = Column(String(255), nullable=False)  # Ministry or Dept
    circular_number = Column(String(100), nullable=False, index=True)
    notification_date = Column(Date, nullable=True)
    official_url = Column(String(500), nullable=False)
    document_checksum = Column(String(64), nullable=True)  # SHA-256 for audit integrity
    file_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    scholarships = relationship("Scholarship", back_populates="official_source")
    government_schemes = relationship("GovernmentScheme", back_populates="official_source")
    eligibility_rules = relationship("EligibilityRule", back_populates="source")
    extracted_evidence = relationship("ExtractedEvidence", back_populates="official_source")

    def __repr__(self) -> str:
        return f"<OfficialSource {self.id}: {self.circular_number} - {self.issuing_authority}>"

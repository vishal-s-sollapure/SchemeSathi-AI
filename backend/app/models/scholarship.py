from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class Scholarship(Base, TimestampMixin):
    """Verified student scholarship registry model for ScholarReady."""
    __tablename__ = "scholarships"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    official_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), default="Education & Scholarships", nullable=False, index=True)
    description = Column(Text, nullable=False)
    government_department = Column(String(255), nullable=False, index=True)
    official_source_url = Column(String(500), nullable=False)
    application_url = Column(String(500), nullable=True)
    academic_cycle = Column(String(50), nullable=True)  # e.g., "2025-26"
    verification_date = Column(Date, nullable=False)
    publication_date = Column(Date, nullable=True)
    information_status = Column(String(50), default="VERIFIED", nullable=False, index=True)  # VERIFIED, DRAFT, ARCHIVED, NEEDS_UPDATE

    # Domain specific metadata
    level = Column(String(100), default="National / Central", nullable=False)  # National / Central, State Gov, Institutional / Merit
    target_audience = Column(String(255), nullable=True)
    course_level = Column(String(100), nullable=False)  # Pre-Matric, Post-Matric, Undergraduate, etc.
    max_annual_income = Column(Float, nullable=False, default=0.0)  # Income cap in INR (0 = no cap)
    min_percentage = Column(Float, default=0.0, nullable=False)
    eligible_categories = Column(JSON, default=list, nullable=False)  # ['SC', 'ST', 'OBC', 'General', 'EWS', 'Minority']
    benefit_amount_annual = Column(String(150), nullable=False)
    application_deadline = Column(String(100), nullable=True)

    official_source_id = Column(String(50), ForeignKey("official_sources.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    official_source = relationship("OfficialSource", back_populates="scholarships")
    eligibility_rules = relationship("EligibilityRule", back_populates="scholarship", cascade="all, delete-orphan")
    requirements = relationship("Requirement", back_populates="scholarship", cascade="all, delete-orphan")
    application_checklists = relationship("ApplicationChecklist", back_populates="scholarship", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Scholarship {self.id}: {self.official_name} ({self.information_status})>"

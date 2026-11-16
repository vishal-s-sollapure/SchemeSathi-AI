from sqlalchemy import Column, Date, ForeignKey, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class GovernmentScheme(Base, TimestampMixin):
    """Verified civic welfare scheme and subsidy registry model for SchemeSathi."""
    __tablename__ = "government_schemes"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    official_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # Agriculture, Healthcare, MSME, Housing, etc.
    description = Column(Text, nullable=False)
    government_department = Column(String(255), nullable=False, index=True)
    official_source_url = Column(String(500), nullable=False)
    application_url = Column(String(500), nullable=True)
    policy_cycle = Column(String(100), nullable=True)  # e.g., "Continuous (FY 2025-26)"
    verification_date = Column(Date, nullable=False)
    publication_date = Column(Date, nullable=True)
    information_status = Column(String(50), default="VERIFIED", nullable=False, index=True)  # VERIFIED, DRAFT, ARCHIVED, NEEDS_UPDATE

    # Domain specific metadata
    level = Column(String(100), default="Central", nullable=False)  # Central, State (Karnataka), etc.
    benefit_type = Column(String(100), nullable=False)  # Direct Benefit Transfer (DBT), Subsidy, Health Insurance Cover, etc.
    annual_benefit = Column(String(255), nullable=False)
    target_beneficiaries = Column(String(255), nullable=False)
    application_deadline = Column(String(100), nullable=True)

    official_source_id = Column(String(50), ForeignKey("official_sources.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    official_source = relationship("OfficialSource", back_populates="government_schemes")
    eligibility_rules = relationship("EligibilityRule", back_populates="scheme", cascade="all, delete-orphan")
    requirements = relationship("Requirement", back_populates="scheme", cascade="all, delete-orphan")
    application_checklists = relationship("ApplicationChecklist", back_populates="scheme", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<GovernmentScheme {self.id}: {self.official_name} ({self.category})>"

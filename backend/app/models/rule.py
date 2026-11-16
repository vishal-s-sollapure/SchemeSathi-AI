from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class EligibilityRule(Base, TimestampMixin):
    """Deterministic, auditable eligibility rule mapped directly to official government clauses."""
    __tablename__ = "eligibility_rules"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    requirement_description = Column(String(500), nullable=False)
    rule_type = Column(String(100), nullable=False, index=True)  # INCOME_CAP, CASTE_CRITERION, DOMICILE, MARKS, AGE, EXCLUSION
    structured_condition = Column(JSON, nullable=False)  # {"field": "annual_family_income", "operator": "LTE", "value": 250000}
    
    # Official source traceability
    source_id = Column(String(50), ForeignKey("official_sources.id", ondelete="RESTRICT"), nullable=False)
    page_number = Column(String(50), nullable=True)  # e.g., "12" or "Annexure-I"
    clause_or_section = Column(String(150), nullable=False)  # e.g., "Section 4.1 Clause (b)"
    applicable_cycle = Column(String(50), nullable=False)  # e.g., "2025-26"

    # Associations
    scholarship_id = Column(String(50), ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=True, index=True)
    scheme_id = Column(String(50), ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=True, index=True)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    failure_guidance = Column(Text, nullable=True)

    # Relationships
    source = relationship("OfficialSource", back_populates="eligibility_rules")
    scholarship = relationship("Scholarship", back_populates="eligibility_rules")
    scheme = relationship("GovernmentScheme", back_populates="eligibility_rules")

    def __repr__(self) -> str:
        return f"<EligibilityRule {self.id}: {self.rule_type} ({self.clause_or_section})>"


class Requirement(Base, TimestampMixin):
    """Official documentation and pre-requisite requirement for a scheme or scholarship."""
    __tablename__ = "requirements"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    scholarship_id = Column(String(50), ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=True, index=True)
    scheme_id = Column(String(50), ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=True, index=True)

    document_type = Column(String(100), nullable=False, index=True)  # INCOME_CERT, CASTE_CERT, BONAFIDE, PASSBOOK, LAND_RECORD
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    issuing_authority = Column(String(255), nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    verification_criteria = Column(JSON, default=dict, nullable=False)  # e.g., {"requires_rd_number": true, "max_age_months": 12}

    # Relationships
    scholarship = relationship("Scholarship", back_populates="requirements")
    scheme = relationship("GovernmentScheme", back_populates="requirements")

    def __repr__(self) -> str:
        return f"<Requirement {self.id}: {self.title} (Mandatory: {self.is_mandatory})>"

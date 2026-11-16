from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class ApplicationChecklist(Base, TimestampMixin):
    """Dynamic application-readiness checklist generated for a student or citizen against a target opportunity."""
    __tablename__ = "application_checklists"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    citizen_profile_id = Column(String(36), ForeignKey("citizen_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    scholarship_id = Column(String(50), ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=True, index=True)
    scheme_id = Column(String(50), ForeignKey("government_schemes.id", ondelete="CASCADE"), nullable=True, index=True)

    readiness_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0%
    overall_status = Column(String(50), default="IN_PROGRESS", nullable=False)  # NOT_STARTED, IN_PROGRESS, READY, ACTION_REQUIRED
    checklist_items = Column(JSON, default=list, nullable=False)
    # checklist_items schema:
    # [
    #   {
    #     "requirement_id": "REQ-...",
    #     "name": "Family Income Certificate",
    #     "status": "ready" | "expiring" | "missing",
    #     "issuing_office": "Tahsildar / Nadakacheri",
    #     "document_id": "DOC-...",
    #     "notes": "Valid till March 2026"
    #   }
    # ]

    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="application_checklists")
    student_profile = relationship("StudentProfile", back_populates="application_checklists")
    citizen_profile = relationship("CitizenProfile", back_populates="application_checklists")
    scholarship = relationship("Scholarship", back_populates="application_checklists")
    scheme = relationship("GovernmentScheme", back_populates="application_checklists")

    def __repr__(self) -> str:
        return f"<ApplicationChecklist {self.id}: Score={self.readiness_score}% ({self.overall_status})>"

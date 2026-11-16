from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class StudentProfile(Base, TimestampMixin):
    """Student profile capturing academic, demographic, and socioeconomic indicators for ScholarReady."""
    __tablename__ = "student_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True, index=True)

    full_name = Column(String(255), nullable=False)
    domicile_state = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # General, OBC, SC, ST, EWS, Minority
    annual_family_income = Column(Float, nullable=False, index=True)  # in INR
    current_course = Column(String(150), nullable=False)
    year_of_study = Column(String(50), nullable=False)
    marks_percentage = Column(Float, nullable=False)
    gender = Column(String(50), nullable=False)
    disability_status = Column(Boolean, default=False, nullable=False)
    hosteller_status = Column(String(50), default="Day Scholar", nullable=False)  # Day Scholar, Hosteller
    extra_attributes = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    uploaded_documents = relationship("UploadedDocument", back_populates="student_profile", cascade="all, delete-orphan")
    application_checklists = relationship("ApplicationChecklist", back_populates="student_profile", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StudentProfile {self.id}: {self.full_name} ({self.category}, Income: ₹{self.annual_family_income})>"


class CitizenProfile(Base, TimestampMixin):
    """Citizen profile capturing demographic, occupational, and vulnerability markers for SchemeSathi."""
    __tablename__ = "citizen_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True, index=True)

    full_name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    domicile_state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    area_type = Column(String(50), default="Rural", nullable=False)  # Rural, Urban
    occupation = Column(String(100), nullable=False, index=True)  # Farmer, Artisan, Daily Wage, Self-Employed, etc.
    annual_family_income = Column(Float, nullable=False, index=True)  # in INR
    social_category = Column(String(50), nullable=False, index=True)  # General, OBC, SC, ST, EWS
    landholding_hectares = Column(Float, default=0.0, nullable=True)
    is_income_tax_payer = Column(Boolean, default=False, nullable=False)
    is_differently_abled = Column(Boolean, default=False, nullable=False)
    bpl_card_holder = Column(Boolean, default=False, nullable=False)
    extra_attributes = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="citizen_profile")
    uploaded_documents = relationship("UploadedDocument", back_populates="citizen_profile", cascade="all, delete-orphan")
    application_checklists = relationship("ApplicationChecklist", back_populates="citizen_profile", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CitizenProfile {self.id}: {self.full_name} ({self.occupation}, State: {self.domicile_state})>"

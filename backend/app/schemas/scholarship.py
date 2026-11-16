from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.common import InformationStatus
from app.schemas.rule import EligibilityRuleResponse, RequirementResponse
from app.schemas.source import OfficialSourceResponse


class ScholarshipBase(BaseModel):
    official_name: str = Field(..., max_length=255)
    category: str = Field("Education & Scholarships", max_length=100)
    description: str
    government_department: str = Field(..., max_length=255)
    official_source_url: str = Field(..., max_length=500)
    application_url: Optional[str] = Field(None, max_length=500)
    academic_cycle: Optional[str] = Field(None, max_length=50)
    verification_date: date
    publication_date: Optional[date] = None
    information_status: InformationStatus = InformationStatus.VERIFIED

    level: str = Field("National / Central", max_length=100)
    target_audience: Optional[str] = None
    course_level: str = Field(..., max_length=100)
    max_annual_income: float = Field(0.0, ge=0)
    min_percentage: float = Field(0.0, ge=0, le=100)
    eligible_categories: List[str] = Field(default_factory=list)
    benefit_amount_annual: str = Field(..., max_length=150)
    application_deadline: Optional[str] = None
    official_source_id: Optional[str] = None


class ScholarshipCreate(ScholarshipBase):
    id: Optional[str] = None


class ScholarshipUpdate(BaseModel):
    official_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    government_department: Optional[str] = None
    official_source_url: Optional[str] = None
    application_url: Optional[str] = None
    academic_cycle: Optional[str] = None
    verification_date: Optional[date] = None
    publication_date: Optional[date] = None
    information_status: Optional[InformationStatus] = None
    level: Optional[str] = None
    target_audience: Optional[str] = None
    course_level: Optional[str] = None
    max_annual_income: Optional[float] = None
    min_percentage: Optional[float] = None
    eligible_categories: Optional[List[str]] = None
    benefit_amount_annual: Optional[str] = None
    application_deadline: Optional[str] = None
    official_source_id: Optional[str] = None


class ScholarshipResponse(ScholarshipBase):
    id: str
    created_at: datetime
    updated_at: datetime
    official_source: Optional[OfficialSourceResponse] = None
    eligibility_rules: List[EligibilityRuleResponse] = []
    requirements: List[RequirementResponse] = []

    class Config:
        from_attributes = True


class ScholarshipFilter(BaseModel):
    search: Optional[str] = None
    level: Optional[str] = None
    category: Optional[str] = None
    course_level: Optional[str] = None
    max_income: Optional[float] = None
    information_status: Optional[InformationStatus] = None

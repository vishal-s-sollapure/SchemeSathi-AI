from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.common import InformationStatus
from app.schemas.rule import EligibilityRuleResponse, RequirementResponse
from app.schemas.source import OfficialSourceResponse


class GovernmentSchemeBase(BaseModel):
    official_name: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    description: str
    government_department: str = Field(..., max_length=255)
    official_source_url: str = Field(..., max_length=500)
    application_url: Optional[str] = Field(None, max_length=500)
    policy_cycle: Optional[str] = Field(None, max_length=100)
    verification_date: date
    publication_date: Optional[date] = None
    information_status: InformationStatus = InformationStatus.VERIFIED

    level: str = Field("Central", max_length=100)
    benefit_type: str = Field(..., max_length=100)
    annual_benefit: str = Field(..., max_length=255)
    target_beneficiaries: str = Field(..., max_length=255)
    application_deadline: Optional[str] = None
    official_source_id: Optional[str] = None


class GovernmentSchemeCreate(GovernmentSchemeBase):
    id: Optional[str] = None


class GovernmentSchemeUpdate(BaseModel):
    official_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    government_department: Optional[str] = None
    official_source_url: Optional[str] = None
    application_url: Optional[str] = None
    policy_cycle: Optional[str] = None
    verification_date: Optional[date] = None
    publication_date: Optional[date] = None
    information_status: Optional[InformationStatus] = None
    level: Optional[str] = None
    benefit_type: Optional[str] = None
    annual_benefit: Optional[str] = None
    target_beneficiaries: Optional[str] = None
    application_deadline: Optional[str] = None
    official_source_id: Optional[str] = None


class GovernmentSchemeResponse(GovernmentSchemeBase):
    id: str
    created_at: datetime
    updated_at: datetime
    official_source: Optional[OfficialSourceResponse] = None
    eligibility_rules: List[EligibilityRuleResponse] = []
    requirements: List[RequirementResponse] = []

    class Config:
        from_attributes = True


class GovernmentSchemeFilter(BaseModel):
    search: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    benefit_type: Optional[str] = None
    information_status: Optional[InformationStatus] = None

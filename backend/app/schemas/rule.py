from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StructuredCondition(BaseModel):
    field: str = Field(..., description="Target profile field e.g. annual_family_income, category, marks_percentage")
    operator: str = Field(..., description="LTE, GTE, EQ, NEQ, IN, NOT_IN, CONTAINS")
    value: Any = Field(..., description="Comparison scalar or list")


class EligibilityRuleBase(BaseModel):
    requirement_description: str = Field(..., max_length=500)
    rule_type: str = Field(..., max_length=100)  # INCOME_CAP, CASTE_CRITERION, DOMICILE, MARKS, AGE, EXCLUSION
    structured_condition: Dict[str, Any]
    source_id: str
    page_number: Optional[str] = None
    clause_or_section: str = Field(..., max_length=150)
    applicable_cycle: str = Field(..., max_length=50)
    is_mandatory: bool = True
    failure_guidance: Optional[str] = None


class EligibilityRuleCreate(EligibilityRuleBase):
    id: Optional[str] = None
    scholarship_id: Optional[str] = None
    scheme_id: Optional[str] = None


class EligibilityRuleUpdate(BaseModel):
    requirement_description: Optional[str] = None
    rule_type: Optional[str] = None
    structured_condition: Optional[Dict[str, Any]] = None
    source_id: Optional[str] = None
    page_number: Optional[str] = None
    clause_or_section: Optional[str] = None
    applicable_cycle: Optional[str] = None
    is_mandatory: Optional[bool] = None
    failure_guidance: Optional[str] = None


class EligibilityRuleResponse(EligibilityRuleBase):
    id: str
    scholarship_id: Optional[str] = None
    scheme_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Requirement Schemas
class RequirementBase(BaseModel):
    document_type: str = Field(..., max_length=100)
    title: str = Field(..., max_length=255)
    description: str
    issuing_authority: str = Field(..., max_length=255)
    is_mandatory: bool = True
    verification_criteria: Dict[str, Any] = Field(default_factory=dict)


class RequirementCreate(RequirementBase):
    id: Optional[str] = None
    scholarship_id: Optional[str] = None
    scheme_id: Optional[str] = None


class RequirementUpdate(BaseModel):
    document_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    issuing_authority: Optional[str] = None
    is_mandatory: Optional[bool] = None
    verification_criteria: Optional[Dict[str, Any]] = None


class RequirementResponse(RequirementBase):
    id: str
    scholarship_id: Optional[str] = None
    scheme_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

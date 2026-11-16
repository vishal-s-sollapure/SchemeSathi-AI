from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


# Student Profile Schemas
class StudentProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    domicile_state: str = Field(..., max_length=100)
    category: str = Field(..., description="General, OBC, SC, ST, EWS, Minority")
    annual_family_income: float = Field(..., ge=0, description="Annual family income in INR")
    current_course: str = Field(..., max_length=150)
    year_of_study: str = Field(..., max_length=50)
    marks_percentage: float = Field(..., ge=0, le=100)
    gender: str = Field(..., max_length=50)
    disability_status: bool = False
    hosteller_status: str = Field("Day Scholar", description="Day Scholar or Hosteller")
    extra_attributes: Dict[str, Any] = Field(default_factory=dict)


class StudentProfileCreate(StudentProfileBase):
    user_id: Optional[str] = None


class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    domicile_state: Optional[str] = None
    category: Optional[str] = None
    annual_family_income: Optional[float] = None
    current_course: Optional[str] = None
    year_of_study: Optional[str] = None
    marks_percentage: Optional[float] = None
    gender: Optional[str] = None
    disability_status: Optional[bool] = None
    hosteller_status: Optional[str] = None
    extra_attributes: Optional[Dict[str, Any]] = None


class StudentProfileResponse(StudentProfileBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Citizen Profile Schemas
class CitizenProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    age: int = Field(..., ge=0, le=130)
    gender: str = Field(..., max_length=50)
    domicile_state: str = Field(..., max_length=100)
    district: Optional[str] = None
    area_type: str = Field("Rural", description="Rural or Urban")
    occupation: str = Field(..., max_length=100)
    annual_family_income: float = Field(..., ge=0, description="Annual family income in INR")
    social_category: str = Field(..., description="General, OBC, SC, ST, EWS")
    landholding_hectares: Optional[float] = Field(0.0, ge=0)
    is_income_tax_payer: bool = False
    is_differently_abled: bool = False
    bpl_card_holder: bool = False
    extra_attributes: Dict[str, Any] = Field(default_factory=dict)


class CitizenProfileCreate(CitizenProfileBase):
    user_id: Optional[str] = None


class CitizenProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    domicile_state: Optional[str] = None
    district: Optional[str] = None
    area_type: Optional[str] = None
    occupation: Optional[str] = None
    annual_family_income: Optional[float] = None
    social_category: Optional[str] = None
    landholding_hectares: Optional[float] = None
    is_income_tax_payer: bool = None
    is_differently_abled: bool = None
    bpl_card_holder: bool = None
    extra_attributes: Optional[Dict[str, Any]] = None


class CitizenProfileResponse(CitizenProfileBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

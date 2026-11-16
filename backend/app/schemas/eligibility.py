from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import EligibilityEvaluationStatus


class StudentEvaluationInput(BaseModel):
    """Student profile input for deterministic eligibility evaluation."""
    full_name: Optional[str] = Field(None, max_length=255)
    age: Optional[int] = Field(None, ge=1, le=120)
    domicile_state: Optional[str] = Field(None, description="State of permanent domicile e.g. Karnataka")
    district: Optional[str] = Field(None, description="Home district where relevant")
    course_level: Optional[str] = Field(None, description="e.g. Undergraduate, Technical / Professional")
    current_course: Optional[str] = Field(None, description="e.g. B.Tech Computer Science, B.Sc, MBBS")
    institution_name: Optional[str] = Field(None, description="Name of college or university")
    institution_type: Optional[str] = Field(
        None, description="e.g. AICTE_APPROVED, RECOGNIZED_UNIVERSITY, GOVT_COLLEGE"
    )
    year_of_study: Optional[str] = Field(None, description="e.g. 1st Year, 2nd Year")
    marks_percentage: Optional[float] = Field(
        None, description="Aggregate marks percentage or percentile in qualifying board exam"
    )
    annual_family_income: Optional[float] = Field(
        None, description="Total annual family income from all sources in INR"
    )
    category: Optional[str] = Field(
        None, description="Social category: General, OBC, SC, ST, EWS, Minority"
    )
    gender: Optional[str] = Field(
        None, description="Gender: Female, Male, Other"
    )
    other_scholarship_recipient: Optional[bool] = Field(
        None, description="Whether currently availing another central/state government scholarship"
    )
    eligible_daughters_count: Optional[int] = Field(
        None, description="Number of daughters in family applying for assistance"
    )
    extra_attributes: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="ignore")


class RuleAssessmentItem(BaseModel):
    """Assessment of a single deterministic eligibility rule."""
    rule_id: str
    requirement_description: str
    rule_type: str
    official_condition: Dict[str, Any]
    user_provided_value: Optional[Any] = None
    status: EligibilityEvaluationStatus
    is_mandatory: bool
    explanation: str
    official_source_title: str
    circular_number: str
    clause_or_section: str
    page_number: Optional[str] = None
    official_source_url: str

    model_config = ConfigDict(from_attributes=True)


class ScholarshipEvaluationResult(BaseModel):
    """Comprehensive evaluation result for a single scholarship."""
    scholarship_id: str
    official_name: str
    government_department: str
    benefit_amount_annual: str
    official_source_url: str
    application_url: Optional[str] = None
    application_deadline: Optional[str] = None
    overall_status: EligibilityEvaluationStatus
    match_score: float = Field(..., ge=0.0, le=100.0, description="Percentage of evaluated rules met")
    
    # Requirement breakdowns
    requirements_satisfied: List[RuleAssessmentItem] = Field(default_factory=list)
    requirements_not_satisfied: List[RuleAssessmentItem] = Field(default_factory=list)
    missing_information: List[RuleAssessmentItem] = Field(default_factory=list)
    conditions_under_review: List[RuleAssessmentItem] = Field(default_factory=list)
    
    # Actionable guidance
    suggested_next_actions: List[str] = Field(default_factory=list)
    required_documents: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ScholarReadyEvaluationSummary(BaseModel):
    """Summary of all evaluated scholarships for a student profile."""
    student_name: Optional[str] = None
    total_scholarships_evaluated: int
    eligible_count: int
    missing_info_count: int
    ineligible_count: int
    under_review_count: int
    scholarships: List[ScholarshipEvaluationResult]
    evaluated_at: str

    model_config = ConfigDict(from_attributes=True)

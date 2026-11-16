from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.eligibility import (
    CitizenEvaluationInput,
    ScholarReadyEvaluationSummary,
    ScholarshipEvaluationResult,
    SchemeDiscoverySummary,
    SchemeEvaluationResult,
    SensitiveFieldExplanation,
    StudentEvaluationInput,
)
from app.schemas.scholarship import ScholarshipFilter
from app.schemas.scheme import GovernmentSchemeFilter
from app.services.opportunity_service import OpportunityService
from app.services.rule_engine import DeterministicRuleEngine

router = APIRouter(prefix="/eligibility", tags=["Eligibility & Discovery Engine"])


# ============================================================================
# ScholarReady Endpoints
# ============================================================================

@router.post(
    "/evaluate-scholarship/{scholarship_id}",
    response_model=ScholarshipEvaluationResult,
    status_code=status.HTTP_200_OK,
)
def evaluate_single_scholarship(
    scholarship_id: str,
    profile_input: StudentEvaluationInput,
    db: Session = Depends(get_db),
):
    """Evaluates a student profile against a specific verified scholarship."""
    service = OpportunityService(db)
    scholarship = service.get_scholarship(scholarship_id)
    return DeterministicRuleEngine.evaluate_scholarship(scholarship, profile_input)


@router.post(
    "/evaluate-scholarships",
    response_model=ScholarReadyEvaluationSummary,
    status_code=status.HTTP_200_OK,
)
def evaluate_all_scholarships(
    profile_input: StudentEvaluationInput,
    db: Session = Depends(get_db),
):
    """Evaluates a student profile across all active scholarships in the catalog.
    
    Returns a prioritized breakdown with exact requirement statuses:
    - MEETS_REQUIREMENT
    - DOES_NOT_MEET_REQUIREMENT
    - MISSING_INFORMATION
    - NEEDS_REVIEW
    """
    service = OpportunityService(db)
    scholarships = service.list_scholarships(ScholarshipFilter(), skip=0, limit=100)
    return DeterministicRuleEngine.evaluate_all_scholarships(scholarships, profile_input)


# ============================================================================
# SchemeSathi Scheme Discovery Endpoints
# ============================================================================

@router.get(
    "/sensitive-fields",
    response_model=List[SensitiveFieldExplanation],
    status_code=status.HTTP_200_OK,
)
def get_sensitive_fields_explanation():
    """Provides civic rationale and legal citations for sensitive profile questions."""
    return DeterministicRuleEngine.get_sensitive_fields_explanation()


@router.post(
    "/evaluate-scheme/{scheme_id}",
    response_model=SchemeEvaluationResult,
    status_code=status.HTTP_200_OK,
)
def evaluate_single_scheme(
    scheme_id: str,
    profile_input: CitizenEvaluationInput,
    db: Session = Depends(get_db),
):
    """Evaluates a citizen profile against a specific verified government scheme."""
    service = OpportunityService(db)
    scheme = service.get_scheme(scheme_id)
    return DeterministicRuleEngine.evaluate_scheme(scheme, profile_input)


@router.post(
    "/discover-schemes",
    response_model=SchemeDiscoverySummary,
    status_code=status.HTTP_200_OK,
)
def discover_schemes(
    profile_input: CitizenEvaluationInput,
    search: Optional[str] = Query(None, description="Keyword search across scheme title, description and ministry"),
    category: Optional[str] = Query(None, description="Filter by scheme category e.g. Agriculture, Social Security"),
    level: Optional[str] = Query(None, description="Central or State (Karnataka)"),
    benefit_type: Optional[str] = Query(None, description="Direct Benefit Transfer (DBT), Subsidy, etc."),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Personalized Government Scheme Discovery for citizens.
    
    Filters available verified government schemes, deterministically evaluates
    structured eligibility rules (never using an LLM), and returns prioritized,
    evidence-backed scheme recommendations with official citations.
    """
    service = OpportunityService(db)
    filters = GovernmentSchemeFilter(
        search=search,
        category=category,
        level=level,
        benefit_type=benefit_type,
    )
    schemes = service.list_schemes(filters, skip=skip, limit=limit)
    return DeterministicRuleEngine.evaluate_all_schemes(schemes, profile_input)

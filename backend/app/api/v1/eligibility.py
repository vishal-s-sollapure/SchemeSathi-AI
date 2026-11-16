from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.eligibility import (
    ScholarReadyEvaluationSummary,
    ScholarshipEvaluationResult,
    StudentEvaluationInput,
)
from app.schemas.scholarship import ScholarshipFilter
from app.services.opportunity_service import OpportunityService
from app.services.rule_engine import DeterministicRuleEngine

router = APIRouter(prefix="/eligibility", tags=["ScholarReady Eligibility Engine"])


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

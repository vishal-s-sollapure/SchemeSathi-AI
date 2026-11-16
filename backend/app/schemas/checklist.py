from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


ChecklistItemStatus = Literal[
    "NOT_STARTED",
    "REQUIRED",
    "UPLOADED",
    "CONFIRMED",
    "NEEDS_REVIEW",
    "NOT_APPLICABLE",
]

ChecklistOverallStatus = Literal[
    "NOT_STARTED",
    "IN_PROGRESS",
    "ACTION_REQUIRED",
    "READY_FOR_SUBMISSION",
    "DISQUALIFIED",
]


class ChecklistItem(BaseModel):
    requirement_id: Optional[str] = None
    name: str = Field(..., max_length=255)
    document_type: str = Field("GENERAL_DOCUMENT", max_length=100)
    description: Optional[str] = None
    status: str = Field("REQUIRED", description="NOT_STARTED, REQUIRED, UPLOADED, CONFIRMED, NEEDS_REVIEW, NOT_APPLICABLE")
    is_mandatory: bool = Field(True)
    issuing_office: Optional[str] = None
    document_id: Optional[str] = None
    critical_notes: Optional[str] = None
    confirmed_evidence: Optional[Dict[str, Any]] = None
    official_clause: Optional[str] = None
    verification_advice: Optional[str] = None


class ApplicationChecklistBase(BaseModel):
    user_id: Optional[str] = None
    student_profile_id: Optional[str] = None
    citizen_profile_id: Optional[str] = None
    scholarship_id: Optional[str] = None
    scheme_id: Optional[str] = None
    readiness_score: float = Field(0.0, ge=0.0, le=100.0)
    overall_status: str = Field("IN_PROGRESS", description="NOT_STARTED, IN_PROGRESS, ACTION_REQUIRED, READY_FOR_SUBMISSION, DISQUALIFIED")
    checklist_items: List[ChecklistItem] = Field(default_factory=list)


class ApplicationChecklistCreate(ApplicationChecklistBase):
    id: Optional[str] = None


class ApplicationChecklistUpdate(BaseModel):
    readiness_score: Optional[float] = None
    overall_status: Optional[str] = None
    checklist_items: Optional[List[ChecklistItem]] = None


class ApplicationChecklistResponse(ApplicationChecklistBase):
    id: str
    evaluated_at: datetime
    created_at: datetime
    updated_at: datetime
    unresolved_mandatory_count: int = 0
    is_ready_for_submission: bool = False
    eligibility_summary: Optional[Dict[str, Any]] = None
    disclaimer: str = (
        "Document uploads and checklist tracking do not guarantee final eligibility. "
        "Submission readiness requires official departmental database validation and nodal approval."
    )

    model_config = ConfigDict(from_attributes=True)


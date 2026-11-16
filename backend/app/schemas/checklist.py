from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChecklistItem(BaseModel):
    requirement_id: Optional[str] = None
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: str = Field(..., description="ready, expiring, missing")
    issuing_office: Optional[str] = None
    document_id: Optional[str] = None
    critical_notes: Optional[str] = None


class ApplicationChecklistBase(BaseModel):
    user_id: Optional[str] = None
    student_profile_id: Optional[str] = None
    citizen_profile_id: Optional[str] = None
    scholarship_id: Optional[str] = None
    scheme_id: Optional[str] = None
    readiness_score: float = Field(0.0, ge=0.0, le=100.0)
    overall_status: str = Field("IN_PROGRESS", description="NOT_STARTED, IN_PROGRESS, READY, ACTION_REQUIRED")
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

    class Config:
        from_attributes = True

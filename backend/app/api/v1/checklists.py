from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.checklist import (
    ApplicationChecklistCreate,
    ApplicationChecklistResponse,
    ApplicationChecklistUpdate,
)
from app.services.checklist_service import ChecklistService

router = APIRouter(prefix="/checklists", tags=["Application Checklists"])


@router.post("/generate", response_model=ApplicationChecklistResponse, status_code=status.HTTP_201_CREATED)
def generate_dynamic_checklist(
    student_profile_id: Optional[str] = Query(None),
    citizen_profile_id: Optional[str] = Query(None),
    scholarship_id: Optional[str] = Query(None),
    scheme_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Generates a personalized dynamic checklist based on verified statutory requirements,
    tracking item states (REQUIRED, UPLOADED, CONFIRMED, NEEDS_REVIEW, NOT_APPLICABLE).
    """
    clean_student_id = student_profile_id if isinstance(student_profile_id, str) else None
    clean_citizen_id = citizen_profile_id if isinstance(citizen_profile_id, str) else None
    clean_sch_id = scholarship_id if isinstance(scholarship_id, str) else None
    clean_scheme_id = scheme_id if isinstance(scheme_id, str) else None

    service = ChecklistService(db)
    return service.generate_dynamic_checklist(
        student_profile_id=clean_student_id,
        citizen_profile_id=clean_citizen_id,
        scholarship_id=clean_sch_id,
        scheme_id=clean_scheme_id,
    )


@router.post("", response_model=ApplicationChecklistResponse, status_code=status.HTTP_201_CREATED)
def create_checklist(data: ApplicationChecklistCreate, db: Session = Depends(get_db)):
    service = ChecklistService(db)
    return service.create_checklist(data)


@router.get("/{checklist_id}", response_model=ApplicationChecklistResponse)
def get_checklist(checklist_id: str, db: Session = Depends(get_db)):
    service = ChecklistService(db)
    return service.get_checklist(checklist_id)


@router.put("/{checklist_id}", response_model=ApplicationChecklistResponse)
def update_checklist(checklist_id: str, data: ApplicationChecklistUpdate, db: Session = Depends(get_db)):
    service = ChecklistService(db)
    return service.update_checklist(checklist_id, data)


@router.get("/student/{student_id}", response_model=List[ApplicationChecklistResponse])
def list_student_checklists(student_id: str, db: Session = Depends(get_db)):
    service = ChecklistService(db)
    return service.list_by_student(student_id)


@router.get("/citizen/{citizen_id}", response_model=List[ApplicationChecklistResponse])
def list_citizen_checklists(citizen_id: str, db: Session = Depends(get_db)):
    service = ChecklistService(db)
    return service.list_by_citizen(citizen_id)

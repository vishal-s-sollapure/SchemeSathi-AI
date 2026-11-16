from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.checklist import (
    ApplicationChecklistCreate,
    ApplicationChecklistResponse,
    ApplicationChecklistUpdate,
)
from app.services.checklist_service import ChecklistService

router = APIRouter(prefix="/checklists", tags=["Application Checklists"])


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

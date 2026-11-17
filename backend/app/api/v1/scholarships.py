from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_admin_key
from app.database import get_db
from app.schemas.common import InformationStatus
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipFilter,
    ScholarshipResponse,
    ScholarshipUpdate,
)
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/scholarships", tags=["Scholarships"])


@router.post("", response_model=ScholarshipResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_key)])
def create_scholarship(data: ScholarshipCreate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.create_scholarship(data)


@router.get("", response_model=List[ScholarshipResponse])
def list_scholarships(
    search: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    course_level: Optional[str] = Query(None),
    max_income: Optional[float] = Query(None),
    information_status: Optional[InformationStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = OpportunityService(db)
    filters = ScholarshipFilter(
        search=search,
        level=level,
        category=category,
        course_level=course_level,
        max_income=max_income,
        information_status=information_status,
    )
    return service.list_scholarships(filters, skip=skip, limit=limit)


@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
def get_scholarship(scholarship_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.get_scholarship(scholarship_id)


@router.put("/{scholarship_id}", response_model=ScholarshipResponse, dependencies=[Depends(require_admin_key)])
def update_scholarship(scholarship_id: str, data: ScholarshipUpdate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.update_scholarship(scholarship_id, data)


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin_key)])
def delete_scholarship(scholarship_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    service.delete_scholarship(scholarship_id)

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import InformationStatus
from app.schemas.scheme import (
    GovernmentSchemeCreate,
    GovernmentSchemeFilter,
    GovernmentSchemeResponse,
    GovernmentSchemeUpdate,
)
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])


@router.post("", response_model=GovernmentSchemeResponse, status_code=status.HTTP_201_CREATED)
def create_scheme(data: GovernmentSchemeCreate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.create_scheme(data)


@router.get("", response_model=List[GovernmentSchemeResponse])
def list_schemes(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    benefit_type: Optional[str] = Query(None),
    information_status: Optional[InformationStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = OpportunityService(db)
    filters = GovernmentSchemeFilter(
        search=search,
        category=category,
        level=level,
        benefit_type=benefit_type,
        information_status=information_status,
    )
    return service.list_schemes(filters, skip=skip, limit=limit)


@router.get("/{scheme_id}", response_model=GovernmentSchemeResponse)
def get_scheme(scheme_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.get_scheme(scheme_id)


@router.put("/{scheme_id}", response_model=GovernmentSchemeResponse)
def update_scheme(scheme_id: str, data: GovernmentSchemeUpdate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.update_scheme(scheme_id, data)


@router.delete("/{scheme_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheme(scheme_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    service.delete_scheme(scheme_id)

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_admin_key
from app.database import get_db
from app.schemas.source import (
    OfficialSourceCreate,
    OfficialSourceResponse,
    OfficialSourceUpdate,
)
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/sources", tags=["Official Sources"])


@router.post("", response_model=OfficialSourceResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_key)])
def create_source(data: OfficialSourceCreate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.create_source(data)


@router.get("", response_model=List[OfficialSourceResponse])
def list_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = OpportunityService(db)
    return service.list_sources(skip=skip, limit=limit)


@router.get("/{source_id}", response_model=OfficialSourceResponse)
def get_source(source_id: str, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.get_source(source_id)


@router.put("/{source_id}", response_model=OfficialSourceResponse, dependencies=[Depends(require_admin_key)])
def update_source(source_id: str, data: OfficialSourceUpdate, db: Session = Depends(get_db)):
    service = OpportunityService(db)
    return service.update_source(source_id, data)

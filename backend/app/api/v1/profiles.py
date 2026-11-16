from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.profile import (
    CitizenProfileCreate,
    CitizenProfileResponse,
    CitizenProfileUpdate,
    StudentProfileCreate,
    StudentProfileResponse,
    StudentProfileUpdate,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["Profiles"])


# Student Profile Routes
@router.post("/student", response_model=StudentProfileResponse, status_code=status.HTTP_201_CREATED)
def create_student_profile(data: StudentProfileCreate, db: Session = Depends(get_db)):
    service = ProfileService(db)
    return service.create_student_profile(data)


@router.get("/student", response_model=List[StudentProfileResponse])
def list_student_profiles(
    domicile_state: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    max_income: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = ProfileService(db)
    return service.list_student_profiles(
        domicile_state=domicile_state,
        category=category,
        max_income=max_income,
        skip=skip,
        limit=limit,
    )


@router.get("/student/{profile_id}", response_model=StudentProfileResponse)
def get_student_profile(profile_id: str, db: Session = Depends(get_db)):
    service = ProfileService(db)
    return service.get_student_profile(profile_id)


@router.put("/student/{profile_id}", response_model=StudentProfileResponse)
def update_student_profile(profile_id: str, data: StudentProfileUpdate, db: Session = Depends(get_db)):
    service = ProfileService(db)
    return service.update_student_profile(profile_id, data)


# Citizen Profile Routes
@router.post("/citizen", response_model=CitizenProfileResponse, status_code=status.HTTP_201_CREATED)
def create_citizen_profile(data: CitizenProfileCreate, db: Session = Depends(get_db)):
    service = ProfileService(db)
    return service.create_citizen_profile(data)


@router.get("/citizen", response_model=List[CitizenProfileResponse])
def list_citizen_profiles(
    domicile_state: Optional[str] = Query(None),
    occupation: Optional[str] = Query(None),
    social_category: Optional[str] = Query(None),
    max_income: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = ProfileService(db)
    return service.list_citizen_profiles(
        domicile_state=domicile_state,
        occupation=occupation,
        social_category=social_category,
        max_income=max_income,
        skip=skip,
        limit=limit,
    )


@router.get("/citizen/{profile_id}", response_model=CitizenProfileResponse)
def get_citizen_profile(profile_id: str, db: Session = Depends(get_db)):
    service = ProfileService(db)
    return service.get_citizen_profile(profile_id)


@router.put("/citizen/{profile_id}", response_model=CitizenProfileResponse)
def update_citizen_profile(profile_id: str, data: CitizenProfileUpdate, db: Session = Depends(get_db)):
    service = ProfileService(db)
    return service.update_citizen_profile(profile_id, data)

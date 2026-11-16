from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.profile import CitizenProfile, StudentProfile
from app.repositories.profile_repo import CitizenProfileRepository, StudentProfileRepository
from app.schemas.profile import (
    CitizenProfileCreate,
    CitizenProfileUpdate,
    StudentProfileCreate,
    StudentProfileUpdate,
)


class ProfileService:
    def __init__(self, db: Session):
        self.student_repo = StudentProfileRepository(db)
        self.citizen_repo = CitizenProfileRepository(db)

    # Student Profiles
    def get_student_profile(self, profile_id: str) -> StudentProfile:
        profile = self.student_repo.get_by_id(profile_id)
        if not profile:
            raise EntityNotFoundException("StudentProfile", profile_id)
        return profile

    def get_student_by_user_id(self, user_id: str) -> Optional[StudentProfile]:
        return self.student_repo.get_by_user_id(user_id)

    def list_student_profiles(
        self,
        domicile_state: Optional[str] = None,
        category: Optional[str] = None,
        max_income: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StudentProfile]:
        return self.student_repo.find_by_filters(
            domicile_state=domicile_state,
            category=category,
            max_income=max_income,
            skip=skip,
            limit=limit,
        )

    def create_student_profile(self, data: StudentProfileCreate) -> StudentProfile:
        profile = StudentProfile(**data.model_dump())
        return self.student_repo.create(profile)

    def update_student_profile(self, profile_id: str, data: StudentProfileUpdate) -> StudentProfile:
        profile = self.get_student_profile(profile_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        return self.student_repo.update(profile)

    def delete_student_profile(self, profile_id: str) -> None:
        profile = self.get_student_profile(profile_id)
        self.student_repo.delete(profile)

    # Citizen Profiles
    def get_citizen_profile(self, profile_id: str) -> CitizenProfile:
        profile = self.citizen_repo.get_by_id(profile_id)
        if not profile:
            raise EntityNotFoundException("CitizenProfile", profile_id)
        return profile

    def get_citizen_by_user_id(self, user_id: str) -> Optional[CitizenProfile]:
        return self.citizen_repo.get_by_user_id(user_id)

    def list_citizen_profiles(
        self,
        domicile_state: Optional[str] = None,
        occupation: Optional[str] = None,
        social_category: Optional[str] = None,
        max_income: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CitizenProfile]:
        return self.citizen_repo.find_by_filters(
            domicile_state=domicile_state,
            occupation=occupation,
            social_category=social_category,
            max_income=max_income,
            skip=skip,
            limit=limit,
        )

    def create_citizen_profile(self, data: CitizenProfileCreate) -> CitizenProfile:
        profile = CitizenProfile(**data.model_dump())
        return self.citizen_repo.create(profile)

    def update_citizen_profile(self, profile_id: str, data: CitizenProfileUpdate) -> CitizenProfile:
        profile = self.get_citizen_profile(profile_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        return self.citizen_repo.update(profile)

    def delete_citizen_profile(self, profile_id: str) -> None:
        profile = self.get_citizen_profile(profile_id)
        self.citizen_repo.delete(profile)

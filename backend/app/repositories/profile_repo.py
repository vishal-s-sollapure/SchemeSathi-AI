from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.profile import CitizenProfile, StudentProfile
from app.repositories.base import BaseRepository


class StudentProfileRepository(BaseRepository[StudentProfile]):
    def __init__(self, db: Session):
        super().__init__(StudentProfile, db)

    def get_by_user_id(self, user_id: str) -> Optional[StudentProfile]:
        return self.db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()

    def find_by_filters(
        self,
        domicile_state: Optional[str] = None,
        category: Optional[str] = None,
        max_income: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StudentProfile]:
        query = self.db.query(StudentProfile)
        if domicile_state:
            query = query.filter(StudentProfile.domicile_state == domicile_state)
        if category:
            query = query.filter(StudentProfile.category == category)
        if max_income is not None:
            query = query.filter(StudentProfile.annual_family_income <= max_income)
        return query.offset(skip).limit(limit).all()


class CitizenProfileRepository(BaseRepository[CitizenProfile]):
    def __init__(self, db: Session):
        super().__init__(CitizenProfile, db)

    def get_by_user_id(self, user_id: str) -> Optional[CitizenProfile]:
        return self.db.query(CitizenProfile).filter(CitizenProfile.user_id == user_id).first()

    def find_by_filters(
        self,
        domicile_state: Optional[str] = None,
        occupation: Optional[str] = None,
        social_category: Optional[str] = None,
        max_income: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CitizenProfile]:
        query = self.db.query(CitizenProfile)
        if domicile_state:
            query = query.filter(CitizenProfile.domicile_state == domicile_state)
        if occupation:
            query = query.filter(CitizenProfile.occupation == occupation)
        if social_category:
            query = query.filter(CitizenProfile.social_category == social_category)
        if max_income is not None:
            query = query.filter(CitizenProfile.annual_family_income <= max_income)
        return query.offset(skip).limit(limit).all()

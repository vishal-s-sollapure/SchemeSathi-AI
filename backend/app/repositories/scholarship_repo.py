from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.scholarship import Scholarship
from app.repositories.base import BaseRepository


class ScholarshipRepository(BaseRepository[Scholarship]):
    def __init__(self, db: Session):
        super().__init__(Scholarship, db)

    def get_with_details(self, id: str) -> Optional[Scholarship]:
        return (
            self.db.query(Scholarship)
            .options(
                joinedload(Scholarship.official_source),
                joinedload(Scholarship.eligibility_rules),
                joinedload(Scholarship.requirements),
            )
            .filter(Scholarship.id == id)
            .first()
        )

    def search_and_filter(
        self,
        search: Optional[str] = None,
        level: Optional[str] = None,
        course_level: Optional[str] = None,
        category: Optional[str] = None,
        max_income: Optional[float] = None,
        information_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Scholarship]:
        query = self.db.query(Scholarship).options(
            joinedload(Scholarship.official_source),
            joinedload(Scholarship.eligibility_rules),
            joinedload(Scholarship.requirements),
        )

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Scholarship.official_name.ilike(search_term),
                    Scholarship.description.ilike(search_term),
                    Scholarship.government_department.ilike(search_term),
                )
            )
        if level:
            query = query.filter(Scholarship.level == level)
        if course_level:
            query = query.filter(Scholarship.course_level == course_level)
        if category:
            query = query.filter(Scholarship.category == category)
        if max_income is not None:
            query = query.filter(Scholarship.max_annual_income >= max_income)
        if information_status:
            query = query.filter(Scholarship.information_status == information_status)

        return query.offset(skip).limit(limit).all()

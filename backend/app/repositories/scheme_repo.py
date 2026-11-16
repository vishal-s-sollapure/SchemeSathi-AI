from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.scheme import GovernmentScheme
from app.repositories.base import BaseRepository


class GovernmentSchemeRepository(BaseRepository[GovernmentScheme]):
    def __init__(self, db: Session):
        super().__init__(GovernmentScheme, db)

    def get_with_details(self, id: str) -> Optional[GovernmentScheme]:
        return (
            self.db.query(GovernmentScheme)
            .options(
                joinedload(GovernmentScheme.official_source),
                joinedload(GovernmentScheme.eligibility_rules),
                joinedload(GovernmentScheme.requirements),
            )
            .filter(GovernmentScheme.id == id)
            .first()
        )

    def search_and_filter(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        benefit_type: Optional[str] = None,
        information_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[GovernmentScheme]:
        query = self.db.query(GovernmentScheme).options(
            joinedload(GovernmentScheme.official_source),
            joinedload(GovernmentScheme.eligibility_rules),
            joinedload(GovernmentScheme.requirements),
        )

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    GovernmentScheme.official_name.ilike(search_term),
                    GovernmentScheme.description.ilike(search_term),
                    GovernmentScheme.government_department.ilike(search_term),
                )
            )
        if category:
            query = query.filter(GovernmentScheme.category == category)
        if level:
            query = query.filter(GovernmentScheme.level == level)
        if benefit_type:
            query = query.filter(GovernmentScheme.benefit_type == benefit_type)
        if information_status:
            query = query.filter(GovernmentScheme.information_status == information_status)

        return query.offset(skip).limit(limit).all()

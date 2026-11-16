from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.rule import EligibilityRule, Requirement
from app.repositories.base import BaseRepository


class EligibilityRuleRepository(BaseRepository[EligibilityRule]):
    def __init__(self, db: Session):
        super().__init__(EligibilityRule, db)

    def get_by_scholarship(self, scholarship_id: str) -> List[EligibilityRule]:
        return self.db.query(EligibilityRule).filter(EligibilityRule.scholarship_id == scholarship_id).all()

    def get_by_scheme(self, scheme_id: str) -> List[EligibilityRule]:
        return self.db.query(EligibilityRule).filter(EligibilityRule.scheme_id == scheme_id).all()


class RequirementRepository(BaseRepository[Requirement]):
    def __init__(self, db: Session):
        super().__init__(Requirement, db)

    def get_by_scholarship(self, scholarship_id: str) -> List[Requirement]:
        return self.db.query(Requirement).filter(Requirement.scholarship_id == scholarship_id).all()

    def get_by_scheme(self, scheme_id: str) -> List[Requirement]:
        return self.db.query(Requirement).filter(Requirement.scheme_id == scheme_id).all()

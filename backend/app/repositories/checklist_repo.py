from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.checklist import ApplicationChecklist
from app.repositories.base import BaseRepository


class ApplicationChecklistRepository(BaseRepository[ApplicationChecklist]):
    def __init__(self, db: Session):
        super().__init__(ApplicationChecklist, db)

    def get_by_student_and_scholarship(self, student_id: str, scholarship_id: str) -> Optional[ApplicationChecklist]:
        return (
            self.db.query(ApplicationChecklist)
            .filter(
                ApplicationChecklist.student_profile_id == student_id,
                ApplicationChecklist.scholarship_id == scholarship_id,
            )
            .first()
        )

    def get_by_citizen_and_scheme(self, citizen_id: str, scheme_id: str) -> Optional[ApplicationChecklist]:
        return (
            self.db.query(ApplicationChecklist)
            .filter(
                ApplicationChecklist.citizen_profile_id == citizen_id,
                ApplicationChecklist.scheme_id == scheme_id,
            )
            .first()
        )

    def get_by_student(self, student_id: str) -> List[ApplicationChecklist]:
        return self.db.query(ApplicationChecklist).filter(ApplicationChecklist.student_profile_id == student_id).all()

    def get_by_citizen(self, citizen_id: str) -> List[ApplicationChecklist]:
        return self.db.query(ApplicationChecklist).filter(ApplicationChecklist.citizen_profile_id == citizen_id).all()

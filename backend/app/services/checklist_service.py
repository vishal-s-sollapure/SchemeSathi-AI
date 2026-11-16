from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.checklist import ApplicationChecklist
from app.repositories.checklist_repo import ApplicationChecklistRepository
from app.repositories.rule_repo import RequirementRepository
from app.schemas.checklist import (
    ApplicationChecklistCreate,
    ApplicationChecklistUpdate,
)
from app.services.document_intelligence.checklist_engine import DynamicChecklistEngine


class ChecklistService:
    def __init__(self, db: Session):
        self.db = db
        self.checklist_repo = ApplicationChecklistRepository(db)
        self.req_repo = RequirementRepository(db)
        self.engine = DynamicChecklistEngine(db)

    def generate_dynamic_checklist(
        self,
        student_profile_id: Optional[str] = None,
        citizen_profile_id: Optional[str] = None,
        scholarship_id: Optional[str] = None,
        scheme_id: Optional[str] = None,
    ) -> ApplicationChecklist:
        """Generates a dynamic checklist based on verified scheme requirements."""
        return self.engine.generate_checklist(
            student_profile_id=student_profile_id,
            citizen_profile_id=citizen_profile_id,
            scholarship_id=scholarship_id,
            scheme_id=scheme_id,
        )

    def get_checklist(self, checklist_id: str) -> ApplicationChecklist:
        checklist = self.checklist_repo.get_by_id(checklist_id)
        if not checklist:
            raise EntityNotFoundException("ApplicationChecklist", checklist_id)
        return checklist

    def create_checklist(self, data: ApplicationChecklistCreate) -> ApplicationChecklist:
        checklist = ApplicationChecklist(
            id=data.id,
            user_id=data.user_id,
            student_profile_id=data.student_profile_id,
            citizen_profile_id=data.citizen_profile_id,
            scholarship_id=data.scholarship_id,
            scheme_id=data.scheme_id,
            readiness_score=data.readiness_score,
            overall_status=data.overall_status,
            checklist_items=[item.model_dump() for item in data.checklist_items],
            evaluated_at=datetime.now(timezone.utc),
        )
        return self.checklist_repo.create(checklist)

    def update_checklist(self, checklist_id: str, data: ApplicationChecklistUpdate) -> ApplicationChecklist:
        checklist = self.get_checklist(checklist_id)
        if data.readiness_score is not None:
            checklist.readiness_score = data.readiness_score
        if data.overall_status is not None:
            checklist.overall_status = data.overall_status
        if data.checklist_items is not None:
            checklist.checklist_items = [item.model_dump() for item in data.checklist_items]
        checklist.evaluated_at = datetime.now(timezone.utc)
        return self.checklist_repo.update(checklist)

    def list_by_student(self, student_id: str) -> List[ApplicationChecklist]:
        return self.checklist_repo.get_by_student(student_id)

    def list_by_citizen(self, citizen_id: str) -> List[ApplicationChecklist]:
        return self.checklist_repo.get_by_citizen(citizen_id)

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.document import ExtractedEvidence, UploadedDocument
from app.repositories.base import BaseRepository


class UploadedDocumentRepository(BaseRepository[UploadedDocument]):
    def __init__(self, db: Session):
        super().__init__(UploadedDocument, db)

    def get_with_evidence(self, id: str) -> Optional[UploadedDocument]:
        return (
            self.db.query(UploadedDocument)
            .options(joinedload(UploadedDocument.extracted_evidence))
            .filter(UploadedDocument.id == id)
            .first()
        )

    def get_by_user(self, user_id: str) -> List[UploadedDocument]:
        return self.db.query(UploadedDocument).filter(UploadedDocument.user_id == user_id).all()

    def get_by_student(self, student_profile_id: str) -> List[UploadedDocument]:
        return self.db.query(UploadedDocument).filter(UploadedDocument.student_profile_id == student_profile_id).all()

    def get_by_citizen(self, citizen_profile_id: str) -> List[UploadedDocument]:
        return self.db.query(UploadedDocument).filter(UploadedDocument.citizen_profile_id == citizen_profile_id).all()


class ExtractedEvidenceRepository(BaseRepository[ExtractedEvidence]):
    def __init__(self, db: Session):
        super().__init__(ExtractedEvidence, db)

    def get_by_document(self, document_id: str) -> List[ExtractedEvidence]:
        return self.db.query(ExtractedEvidence).filter(ExtractedEvidence.document_id == document_id).all()

from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.document import ExtractedEvidence, UploadedDocument
from app.repositories.document_repo import ExtractedEvidenceRepository, UploadedDocumentRepository
from app.schemas.document import (
    ExtractedEvidenceCreate,
    UploadedDocumentCreate,
)


class DocumentService:
    def __init__(self, db: Session):
        self.doc_repo = UploadedDocumentRepository(db)
        self.evidence_repo = ExtractedEvidenceRepository(db)

    def get_document(self, doc_id: str) -> UploadedDocument:
        doc = self.doc_repo.get_with_evidence(doc_id)
        if not doc:
            raise EntityNotFoundException("UploadedDocument", doc_id)
        return doc

    def list_documents_for_user(self, user_id: str) -> List[UploadedDocument]:
        return self.doc_repo.get_by_user(user_id)

    def list_documents_for_student(self, student_id: str) -> List[UploadedDocument]:
        return self.doc_repo.get_by_student(student_id)

    def list_documents_for_citizen(self, citizen_id: str) -> List[UploadedDocument]:
        return self.doc_repo.get_by_citizen(citizen_id)

    def create_document_record(self, data: UploadedDocumentCreate) -> UploadedDocument:
        doc = UploadedDocument(**data.model_dump())
        return self.doc_repo.create(doc)

    def update_processing_status(self, doc_id: str, status: str) -> UploadedDocument:
        doc = self.get_document(doc_id)
        doc.processing_status = status
        return self.doc_repo.update(doc)

    def add_extracted_evidence(self, data: ExtractedEvidenceCreate) -> ExtractedEvidence:
        self.get_document(data.document_id)
        evidence = ExtractedEvidence(**data.model_dump())
        return self.evidence_repo.create(evidence)

    def get_evidence_for_document(self, doc_id: str) -> List[ExtractedEvidence]:
        return self.evidence_repo.get_by_document(doc_id)

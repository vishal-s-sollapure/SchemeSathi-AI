from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.checklist import ApplicationChecklist
from app.models.document import ExtractedEvidence, UploadedDocument
from app.repositories.checklist_repo import ApplicationChecklistRepository
from app.repositories.document_repo import ExtractedEvidenceRepository, UploadedDocumentRepository
from app.schemas.document import (
    DocumentIntelligenceResponse,
    EvidenceConfirmationItem,
    ExtractedEvidenceCreate,
    ExtractedEvidenceResponse,
    UploadedDocumentCreate,
    UploadedDocumentResponse,
)
from app.services.document_intelligence.checklist_engine import DynamicChecklistEngine
from app.services.document_intelligence.extractor import DocumentIntelligenceExtractor
from app.services.document_intelligence.parser import DocumentParser


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = UploadedDocumentRepository(db)
        self.evidence_repo = ExtractedEvidenceRepository(db)
        self.checklist_repo = ApplicationChecklistRepository(db)

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

    def process_and_upload_document(
        self,
        file_bytes: bytes,
        original_filename: str,
        document_type_hint: Optional[str] = None,
        student_profile_id: Optional[str] = None,
        citizen_profile_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> DocumentIntelligenceResponse:
        """Processes an uploaded PDF, extracts text and metadata, extracts candidate fields,
        and persists structured evidence awaiting user confirmation.
        """
        # 1. Validate & Parse PDF with page tracking & OCR fallback detection
        pages_text, ocr_applied, total_pages = DocumentParser.extract_text_and_metadata(
            file_bytes, original_filename
        )
        sha256 = DocumentParser.calculate_sha256(file_bytes)

        # 2. Heuristic Document Type Classification
        full_text = "\n".join(p["text"] for p in pages_text)
        detected_type = document_type_hint or DocumentIntelligenceExtractor.detect_document_type(full_text)

        # 3. Extract candidate fields across pages
        candidates = DocumentIntelligenceExtractor.extract_candidates_from_pages(pages_text)

        # 4. Save file to secure storage preventing path traversal
        dest_path, _ = DocumentParser.save_file_securely(file_bytes, original_filename)

        # 5. Persist UploadedDocument record
        doc = UploadedDocument(
            user_id=user_id,
            student_profile_id=student_profile_id,
            citizen_profile_id=citizen_profile_id,
            document_type=detected_type,
            original_filename=original_filename,
            storage_path=str(dest_path),
            file_size_bytes=len(file_bytes),
            mime_type="application/pdf",
            sha256_hash=sha256,
            processing_status="PROCESSED",
            page_count=total_pages,
            ocr_applied=ocr_applied,
            extra_metadata={
                "detected_type": detected_type,
                "candidate_count": len(candidates),
                "is_scanned": ocr_applied,
            },
        )
        doc = self.doc_repo.create(doc)

        # 6. Persist ExtractedEvidence candidates awaiting user confirmation
        persisted_evidence: List[ExtractedEvidence] = []
        for cand in candidates:
            ev = ExtractedEvidence(
                document_id=doc.id,
                evidence_type=cand.evidence_type,
                field_key=cand.field_key,
                extracted_value=cand.extracted_value,
                confirmed_value=None,
                is_confirmed=False,
                confidence_score=cand.confidence_score,
                page_number=cand.page_number,
                bounding_box=cand.bounding_box,
                raw_text_snippet=cand.raw_text_snippet,
            )
            persisted_evidence.append(self.evidence_repo.create(ev))

        # Re-fetch document with evidence
        doc = self.get_document(doc.id)

        evidence_responses = [
            ExtractedEvidenceResponse.model_validate(ev) for ev in persisted_evidence
        ]
        doc_response = UploadedDocumentResponse.model_validate(doc)

        return DocumentIntelligenceResponse(
            document=doc_response,
            extracted_candidates=evidence_responses,
            page_count=total_pages,
            ocr_applied=ocr_applied,
            detected_document_type=detected_type,
            disclaimer=DocumentIntelligenceExtractor.DISCLAIMER,
        )

    def confirm_evidence_values(
        self,
        doc_id: str,
        confirmations: List[EvidenceConfirmationItem],
        checklist_id: Optional[str] = None,
    ) -> List[ExtractedEvidenceResponse]:
        """User confirmation of extracted evidence. Confirmed values are stored separately from
        unconfirmed extractions. Triggers checklist synchronization if checklist_id is provided.
        """
        doc = self.get_document(doc_id)
        updated_evidence: List[ExtractedEvidenceResponse] = []

        for conf in confirmations:
            ev = self.evidence_repo.get_by_id(conf.evidence_id)
            if ev and ev.document_id == doc.id:
                ev.confirmed_value = conf.confirmed_value
                ev.is_confirmed = conf.is_confirmed
                ev.confirmed_at = datetime.now(timezone.utc)
                saved_ev = self.evidence_repo.update(ev)
                updated_evidence.append(ExtractedEvidenceResponse.model_validate(saved_ev))

        # If connected to a checklist, update checklist items & recalculate readiness
        if checklist_id:
            checklist_engine = DynamicChecklistEngine(self.db)
            conf_payloads = [item.model_dump() for item in confirmations]
            checklist_engine.confirm_evidence_and_update(checklist_id, doc.id, conf_payloads)

        return updated_evidence

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Safely removes physical file from disk, deletes database records,
        and dynamically updates associated checklist items.
        """
        doc = self.get_document(doc_id)
        storage_path = Path(doc.storage_path)

        # 1. Secure physical file cleanup
        if storage_path.exists():
            try:
                storage_path.unlink(missing_ok=True)
            except Exception as e:
                pass

        # 2. Update any checklists linking to this document
        checklists = self.checklist_repo.list_all()
        for chk in checklists:
            items = list(chk.checklist_items)
            modified = False
            for item in items:
                if item.get("document_id") == doc.id:
                    item["document_id"] = None
                    item["status"] = "REQUIRED" if item.get("is_mandatory", True) else "NOT_STARTED"
                    item["confirmed_evidence"] = None
                    modified = True

            if modified:
                # Recalculate checklist readiness
                engine = DynamicChecklistEngine(self.db)
                readiness_score, overall_status = engine._calculate_readiness(items)
                chk.checklist_items = items
                chk.readiness_score = readiness_score
                chk.overall_status = overall_status
                chk.evaluated_at = datetime.now(timezone.utc)
                self.checklist_repo.update(chk)

        # 3. Delete database record (cascades to extracted_evidence)
        self.doc_repo.delete(doc_id)

        return {
            "status": "DELETED",
            "document_id": doc_id,
            "filename": doc.original_filename,
            "message": "Document and associated evidence successfully deleted and checklist rolled back.",
        }


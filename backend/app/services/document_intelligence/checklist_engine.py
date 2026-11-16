from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.checklist import ApplicationChecklist
from app.models.document import ExtractedEvidence, UploadedDocument
from app.models.profile import CitizenProfile, StudentProfile
from app.models.scholarship import Requirement
from app.repositories.checklist_repo import ApplicationChecklistRepository
from app.repositories.document_repo import ExtractedEvidenceRepository, UploadedDocumentRepository
from app.repositories.profile_repo import CitizenProfileRepository, StudentProfileRepository
from app.repositories.rule_repo import RequirementRepository
from app.schemas.checklist import ChecklistItem
from app.services.rule_engine import ScholarshipRuleEngine

logger = logging.getLogger("checklist_engine")


class DynamicChecklistEngine:
    """Personalized application-readiness checklist and evidence confirmation engine.
    
    Guarantees:
    - Uploading a document never automatically guarantees eligibility.
    - Never marks an application ready while required conditions remain unresolved.
    - Dynamic status tracking: NOT_STARTED, REQUIRED, UPLOADED, CONFIRMED, NEEDS_REVIEW, NOT_APPLICABLE.
    - Re-evaluates deterministic eligibility upon evidence confirmation.
    """

    DISCLAIMER = (
        "Document uploads and checklist tracking do not guarantee final eligibility. "
        "Submission readiness requires official departmental database validation and nodal approval."
    )

    def __init__(self, db: Session):
        self.db = db
        self.checklist_repo = ApplicationChecklistRepository(db)
        self.req_repo = RequirementRepository(db)
        self.doc_repo = UploadedDocumentRepository(db)
        self.evidence_repo = ExtractedEvidenceRepository(db)
        self.student_repo = StudentProfileRepository(db)
        self.citizen_repo = CitizenProfileRepository(db)

    def generate_checklist(
        self,
        student_profile_id: Optional[str] = None,
        citizen_profile_id: Optional[str] = None,
        scholarship_id: Optional[str] = None,
        scheme_id: Optional[str] = None,
    ) -> ApplicationChecklist:
        """Generates or updates a personalized dynamic checklist based on verified scheme requirements."""
        if not scholarship_id and not scheme_id:
            raise ValueError("Either scholarship_id or scheme_id must be provided to generate a checklist.")

        # 1. Fetch requirements
        requirements: List[Requirement] = []
        if scholarship_id:
            requirements = self.req_repo.get_by_scholarship(scholarship_id)
        elif scheme_id:
            requirements = self.req_repo.get_by_scheme(scheme_id)

        # 2. Fetch existing uploaded documents for profile
        existing_docs: List[UploadedDocument] = []
        student_profile: Optional[StudentProfile] = None
        citizen_profile: Optional[CitizenProfile] = None

        if student_profile_id:
            student_profile = self.student_repo.get_by_id(student_profile_id)
            existing_docs = self.doc_repo.get_by_student(student_profile_id)
        elif citizen_profile_id:
            citizen_profile = self.citizen_repo.get_by_id(citizen_profile_id)
            existing_docs = self.doc_repo.get_by_citizen(citizen_profile_id)

        docs_by_type: Dict[str, UploadedDocument] = {doc.document_type.upper(): doc for doc in existing_docs}

        # 3. Construct personalized checklist items
        checklist_items: List[Dict[str, Any]] = []

        for req in requirements:
            doc_type = req.document_type.upper()
            matched_doc = docs_by_type.get(doc_type)

            # Check applicability
            is_applicable = True
            if req.document_type == "CASTE_CERTIFICATE":
                # General category students are not required to provide caste certificates
                category = (
                    (student_profile.category if student_profile else "")
                    or (citizen_profile.social_category if citizen_profile else "")
                )
                if category.upper() in ("GENERAL", "OPEN", "GM"):
                    is_applicable = False

            # Determine item status
            if not is_applicable:
                status = "NOT_APPLICABLE"
            elif not matched_doc:
                status = "REQUIRED" if req.is_mandatory else "NOT_STARTED"
            else:
                # Check if evidence has been confirmed
                evidence_list = self.evidence_repo.get_by_document(matched_doc.id)
                has_confirmed = any(e.is_confirmed for e in evidence_list)
                if has_confirmed:
                    status = "CONFIRMED"
                elif matched_doc.processing_status == "FAILED":
                    status = "NEEDS_REVIEW"
                else:
                    status = "UPLOADED"

            confirmed_data = {}
            if matched_doc:
                ev_list = self.evidence_repo.get_by_document(matched_doc.id)
                for ev in ev_list:
                    if ev.is_confirmed:
                        confirmed_data[ev.field_key or ev.evidence_type] = ev.confirmed_value or ev.extracted_value

            item = ChecklistItem(
                requirement_id=req.id,
                name=req.title,
                document_type=req.document_type,
                description=req.description,
                status=status,
                is_mandatory=req.is_mandatory,
                issuing_office=req.issuing_authority,
                document_id=matched_doc.id if matched_doc else None,
                critical_notes=req.description,
                confirmed_evidence=confirmed_data if confirmed_data else None,
            )
            checklist_items.append(item.model_dump())

        # 4. Compute metrics
        readiness_score, overall_status = self._calculate_readiness(checklist_items)

        checklist = ApplicationChecklist(
            student_profile_id=student_profile_id,
            citizen_profile_id=citizen_profile_id,
            scholarship_id=scholarship_id,
            scheme_id=scheme_id,
            readiness_score=readiness_score,
            overall_status=overall_status,
            checklist_items=checklist_items,
            evaluated_at=datetime.now(timezone.utc),
        )
        return self.checklist_repo.create(checklist)

    def confirm_evidence_and_update(
        self,
        checklist_id: str,
        document_id: str,
        confirmations: List[Dict[str, Any]],
    ) -> ApplicationChecklist:
        """Confirms extracted evidence values, updates applicant profile, recalculates eligibility,
        and dynamically transitions checklist status.
        """
        checklist = self.checklist_repo.get_by_id(checklist_id)
        if not checklist:
            raise EntityNotFoundException("ApplicationChecklist", checklist_id)

        doc = self.doc_repo.get_with_evidence(document_id)
        if not doc:
            raise EntityNotFoundException("UploadedDocument", document_id)

        # 1. Update Extracted Evidence records
        student_profile = (
            self.student_repo.get_by_id(checklist.student_profile_id)
            if checklist.student_profile_id
            else None
        )
        citizen_profile = (
            self.citizen_repo.get_by_id(checklist.citizen_profile_id)
            if checklist.citizen_profile_id
            else None
        )

        for conf in confirmations:
            ev_id = conf.get("evidence_id")
            confirmed_val = conf.get("confirmed_value", "").strip()
            is_confirmed = conf.get("is_confirmed", True)

            evidence = self.evidence_repo.get_by_id(ev_id)
            if evidence and evidence.document_id == document_id:
                evidence.confirmed_value = confirmed_val
                evidence.is_confirmed = is_confirmed
                evidence.confirmed_at = datetime.now(timezone.utc)
                self.evidence_repo.update(evidence)

                # Sync confirmed value to Profile if applicable
                field_key = (evidence.field_key or "").lower()
                self._sync_field_to_profile(student_profile, citizen_profile, field_key, confirmed_val)

        if student_profile:
            self.student_repo.update(student_profile)
        if citizen_profile:
            self.citizen_repo.update(citizen_profile)

        # 2. Update Checklist Item corresponding to this document
        items = list(checklist.checklist_items)
        for item in items:
            if item.get("document_id") == document_id or item.get("document_type") == doc.document_type:
                item["document_id"] = document_id
                item["status"] = "CONFIRMED"
                # Gather all confirmed evidence
                all_ev = self.evidence_repo.get_by_document(document_id)
                item["confirmed_evidence"] = {
                    (e.field_key or e.evidence_type): (e.confirmed_value or e.extracted_value)
                    for e in all_ev
                    if e.is_confirmed
                }

        # 3. Recalculate Readiness & Eligibility
        readiness_score, overall_status = self._calculate_readiness(items)

        # 4. Trigger Deterministic Rule Evaluation if all mandatory items confirmed
        if overall_status == "READY_FOR_SUBMISSION" and checklist.scholarship_id and student_profile:
            rule_engine = ScholarshipRuleEngine(self.db)
            assessment = rule_engine.evaluate_single(student_profile.id, checklist.scholarship_id)
            if assessment.overall_status != "MEETS_REQUIREMENT":
                # Safety constraint: System MUST NOT mark ready while eligibility criteria remain unmet
                overall_status = "ACTION_REQUIRED"

        checklist.checklist_items = items
        checklist.readiness_score = readiness_score
        checklist.overall_status = overall_status
        checklist.evaluated_at = datetime.now(timezone.utc)
        return self.checklist_repo.update(checklist)

    def _sync_field_to_profile(
        self,
        student_profile: Optional[StudentProfile],
        citizen_profile: Optional[CitizenProfile],
        field_key: str,
        confirmed_val: str,
    ) -> None:
        """Syncs user-confirmed document values into structured profile records."""
        if not confirmed_val:
            return

        if "income" in field_key:
            # Parse clean float
            digits = re.sub(r"[^\d.]", "", confirmed_val)
            if digits:
                try:
                    val = float(digits)
                    if student_profile:
                        student_profile.annual_family_income = val
                    if citizen_profile:
                        citizen_profile.annual_family_income = val
                except ValueError:
                    pass

        elif "marks" in field_key or "percentage" in field_key:
            digits = re.sub(r"[^\d.]", "", confirmed_val)
            if digits and student_profile:
                try:
                    val = float(digits)
                    student_profile.marks_percentage = val
                except ValueError:
                    pass

        elif "course" in field_key and student_profile:
            student_profile.current_course = confirmed_val

        elif "institution" in field_key and student_profile:
            student_profile.institution = confirmed_val

        elif "category" in field_key:
            if student_profile:
                student_profile.category = confirmed_val
            if citizen_profile:
                citizen_profile.social_category = confirmed_val

    def _calculate_readiness(self, checklist_items: List[Dict[str, Any]]) -> Tuple[float, str]:
        """Calculates dynamic readiness score and overall submission state.
        
        Guarantees:
        - Readiness score is bounded in [0.0, 100.0].
        - An application is NEVER marked READY_FOR_SUBMISSION if any mandatory requirement is unconfirmed.
        """
        mandatory_items = [i for i in checklist_items if i.get("is_mandatory", True) and i.get("status") != "NOT_APPLICABLE"]
        if not mandatory_items:
            return 100.0, "READY_FOR_SUBMISSION"

        confirmed_count = sum(1 for i in mandatory_items if i.get("status") == "CONFIRMED")
        unresolved_count = len(mandatory_items) - confirmed_count

        score = round((confirmed_count / len(mandatory_items)) * 100.0, 1)

        if unresolved_count == 0:
            overall_status = "READY_FOR_SUBMISSION"
        elif confirmed_count > 0:
            overall_status = "IN_PROGRESS"
        else:
            overall_status = "REQUIRED"

        return score, overall_status

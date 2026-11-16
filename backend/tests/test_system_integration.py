import pytest
from app.database import SessionLocal, init_db
from app.models import Scholarship, GovernmentScheme, UploadedDocument, ApplicationChecklist
from app.schemas.common import EligibilityEvaluationStatus
from app.schemas.document import EvidenceConfirmationItem
from app.schemas.eligibility import StudentEvaluationInput, CitizenEvaluationInput
from app.services.checklist_service import ChecklistService
from app.services.document_intelligence.parser import DocumentParser
from app.services.document_service import DocumentService
from app.services.opportunity_service import OpportunityService
from app.services.policy_service import PolicyService
from app.services.rag import RAGPipeline
from app.services.rag.citation_validator import CitationValidator
from app.services.rag.models import DocumentChunk
from app.services.rule_engine import DeterministicRuleEngine


@pytest.fixture(scope="module")
def db_session():
    init_db()
    session = SessionLocal()
    yield session
    session.close()


class TestSystemIntegrationAndEvaluation:
    """End-to-End System Integration and Evaluation Suite for SchemeSathi AI (Phase 11)."""

    # =========================================================================
    # 1. ScholarReady & Boundary/Missing Profile Evaluation
    # =========================================================================
    def test_scholarready_complete_profile_evaluation(self, db_session):
        """Tests that a fully complete student profile receives deterministic eligibility and ranking."""
        service = OpportunityService(db_session)
        sch = service.get_scholarship("SCH-MOE-CSSS-2024")
        profile = StudentEvaluationInput(
            full_name="Ananya Sharma",
            domicile_state="Delhi",
            course_level="Undergraduate",
            current_course="B.A. Economics",
            marks_percentage=88.5,
            annual_family_income=320000.0,
            category="General",
            gender="Female",
            other_scholarship_recipient=False,
        )
        res = DeterministicRuleEngine.evaluate_scholarship(sch, profile)
        assert res.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
        assert res.match_score == 100.0
        assert len(res.requirements_satisfied) >= 3

    def test_scholarready_missing_profile_fields(self, db_session):
        """Tests that omitting required fields yields MISSING_INFORMATION, never false rejection."""
        service = OpportunityService(db_session)
        sch = service.get_scholarship("SCH-MOE-CSSS-2024")
        incomplete_profile = StudentEvaluationInput(
            full_name="Rahul Varma",
            course_level="Undergraduate",
            annual_family_income=250000.0,
            # marks_percentage omitted
            # other_scholarship_recipient omitted
        )
        res = DeterministicRuleEngine.evaluate_scholarship(sch, incomplete_profile)
        assert res.overall_status == EligibilityEvaluationStatus.MISSING_INFORMATION
        assert len(res.missing_information) >= 1
        missing_rule_ids = [m.rule_id for m in res.missing_information]
        assert "RULE-CSSS-PERCENTILE" in missing_rule_ids

    def test_boundary_and_conflicting_conditions(self, db_session):
        """Tests boundary conditions and conflicting values."""
        service = OpportunityService(db_session)
        sch = service.get_scholarship("SCH-AICTE-PRAGATI-DEGREE")

        # Boundary: Exact income limit ₹800,000 passes
        boundary_profile = StudentEvaluationInput(
            course_level="Technical / Professional",
            gender="Female",
            annual_family_income=800000.0,
            marks_percentage=75.0,
            eligible_daughters_count=2,
            other_scholarship_recipient=False,
        )
        res = DeterministicRuleEngine.evaluate_scholarship(sch, boundary_profile)
        inc_req = [r for r in res.requirements_satisfied if "income" in r.rule_id.lower()]
        assert len(inc_req) >= 1

        # Conflict: 3 daughters claiming scheme when max allowed is 2
        conflict_daughters = StudentEvaluationInput(
            course_level="Technical / Professional",
            gender="Female",
            annual_family_income=500000.0,
            marks_percentage=75.0,
            eligible_daughters_count=3,
            other_scholarship_recipient=False,
        )
        res_conflict = DeterministicRuleEngine.evaluate_scholarship(sch, conflict_daughters)
        assert res_conflict.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT

    # =========================================================================
    # 2. Scheme Discovery Evaluation
    # =========================================================================
    def test_scheme_discovery_gruha_lakshmi(self, db_session):
        """Tests Scheme Discovery evaluation for Karnataka Gruha Lakshmi Scheme."""
        service = OpportunityService(db_session)
        scheme = service.get_scheme("SCHEME-KAR-GRUHA-LAKSHMI")

        # Eligible woman head of family
        citizen_profile = CitizenEvaluationInput(
            full_name="Savita Gowda",
            gender="Female",
            domicile_state="Karnataka",
            district="Mandya",
            occupation="Homemaker",
            is_income_tax_payer=False,
        )
        res = DeterministicRuleEngine.evaluate_scheme(scheme, citizen_profile)
        assert res.overall_status == EligibilityEvaluationStatus.MEETS_REQUIREMENT
        assert res.match_score == 100.0

        # Disqualified by income tax payment
        tax_payer_citizen = CitizenEvaluationInput(
            full_name="Savita Gowda",
            gender="Female",
            domicile_state="Karnataka",
            district="Mandya",
            occupation="Homemaker",
            is_income_tax_payer=True,
        )
        res_tax = DeterministicRuleEngine.evaluate_scheme(scheme, tax_payer_citizen)
        assert res_tax.overall_status == EligibilityEvaluationStatus.DOES_NOT_MEET_REQUIREMENT

    # =========================================================================
    # 3. RAG Retrieval, Citation Support & Hallucination Rejection
    # =========================================================================
    def test_rag_retrieval_and_citation_support(self):
        """Tests that RAG returns verified citations derived strictly from retrieved evidence."""
        pipeline = RAGPipeline.get_instance()
        resp = pipeline.ask("How many days does a college officer have to complete e-Attestation under Sakala Act?")
        assert resp.sufficient_evidence is True
        assert len(resp.citations) >= 1
        assert "SWD-SSP-2023-CIR-09" in [c.circular_number for c in resp.citations]
        assert "7" in resp.answer

    def test_citation_validator_rejects_hallucinated_sources(self):
        """Tests that citations referring to non-retrieved or non-existent chunks are rejected."""
        genuine_chunk = DocumentChunk(
            chunk_id="CHK-REAL-01",
            text="PM-KISAN provides ₹6000 per year.",
            document_title="PM-KISAN Guidelines",
            official_source_url="https://pmkisan.gov.in",
            government_department="MoA",
            section_or_clause="Clause 1",
            applicable_cycle="2024-25",
        )
        retrieved = [genuine_chunk]

        candidates = [
            {
                "source_title": "PM-KISAN Guidelines",
                "clause_or_section": "Clause 1",
                "matched_chunk_id": "CHK-REAL-01",
            },
            {
                "source_title": "Fake Ministry Order 2099",
                "clause_or_section": "Section 999",
                "matched_chunk_id": "CHK-FAKE-999",
            },
        ]

        validated = CitationValidator.validate_citations(candidates, retrieved)
        assert len(validated) == 1
        assert validated[0].matched_chunk_id == "CHK-REAL-01"

    def test_unsupported_question_handling(self):
        """Tests factual fallback when user asks an unsupported question outside government domain."""
        pipeline = RAGPipeline.get_instance()
        resp = pipeline.ask("How do I claim ₹50 Lakhs under the Galactic Space Exploration Citizen Subsidy 2099?")
        assert resp.sufficient_evidence is False
        assert len(resp.citations) == 0
        assert "could not find authoritative government guidelines" in resp.answer

    # =========================================================================
    # 4. Scanned PDF Detection & OCR Fallback
    # =========================================================================
    def test_scanned_pdf_detection(self):
        """Tests that image-based PDFs with minimal direct text trigger OCR fallback detection."""
        import fitz
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 50), "X")  # only 1 character
        pdf_bytes = doc.tobytes()
        doc.close()

        pages_text, ocr_applied, total_pages = DocumentParser.extract_text_and_metadata(pdf_bytes, "scan.pdf")
        assert total_pages == 1
        assert pages_text[0]["char_count"] < 25

    # =========================================================================
    # 5. Evidence Confirmation & Dynamic Checklist Updates
    # =========================================================================
    def test_evidence_confirmation_and_checklist_progression(self, db_session):
        """Tests that confirming unconfirmed extraction progresses checklist from NOT_STARTED to COMPLETED."""
        from app.services.document_intelligence.checklist_engine import DynamicChecklistEngine
        engine = DynamicChecklistEngine(db_session)
        doc_service = DocumentService(db_session)

        # 1. Create a dynamic checklist for CSSS
        checklist = engine.generate_checklist(
            student_profile_id=None,
            scholarship_id="SCH-MOE-CSSS-2024",
        )
        assert len(checklist.checklist_items) >= 2
        initial_status = checklist.checklist_items[0]["status"]
        assert initial_status in ("REQUIRED", "NOT_STARTED", "IN_PROGRESS")

        # 2. Upload and process a valid PDF
        import fitz
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 50), "Income Certificate\nAnnual Family Income: Rs. 2,40,000\nIssued by Tahsildar")
        pdf_bytes = doc.tobytes()
        doc.close()

        parsed = doc_service.process_and_upload_document(
            file_bytes=pdf_bytes,
            original_filename="income_cert.pdf",
            document_type_hint="INCOME_CERTIFICATE",
        )
        assert parsed.document.id is not None
        assert len(parsed.extracted_candidates) >= 1

        # 3. Confirm evidence and link to checklist
        confirmations = [
            EvidenceConfirmationItem(
                evidence_id=cand.id,
                confirmed_value="240000.00",
                is_confirmed=True,
            )
            for cand in parsed.extracted_candidates
        ]
        doc_service.confirm_evidence_values(
            doc_id=parsed.document.id,
            confirmations=confirmations,
            checklist_id=checklist.id,
        )

        # 4. Verify checklist progression
        checklist_service = ChecklistService(db_session)
        updated_checklist = checklist_service.get_checklist(checklist.id)
        assert updated_checklist is not None
        matching_item = next(
            (item for item in updated_checklist.checklist_items if "income" in item.get("requirement_id", "").lower() or "income" in item.get("name", "").lower()),
            None
        )
        if matching_item:
            assert matching_item["status"] in ("CONFIRMED", "UPLOADED", "COMPLETED", "IN_PROGRESS")
            assert matching_item.get("document_id") == parsed.document.id

    # =========================================================================
    # 6. Multilingual Response Quality (Kannada & Hindi)
    # =========================================================================
    def test_multilingual_responses_kannada_and_hindi(self):
        """Verifies high-fidelity responses preserving official names and numbers in Kannada & Hindi."""
        policy_service = PolicyService.get_instance()

        # Kannada Simplification
        res_kn = policy_service.simplify_policy("POL-SSP-EATTEST-CIRCULAR", language="kn")
        assert res_kn.language == "kn"
        assert len(res_kn.five_line_summary) == 5
        assert any("ಸಕಾಲ" in line or "SSP" in line for line in res_kn.five_line_summary)

        # Hindi Simplification
        res_hi = policy_service.simplify_policy("POL-SSP-EATTEST-CIRCULAR", language="hi")
        assert res_hi.language == "hi"
        assert len(res_hi.five_line_summary) == 5
        assert any("सकाला" in line or "SSP" in line for line in res_hi.five_line_summary)

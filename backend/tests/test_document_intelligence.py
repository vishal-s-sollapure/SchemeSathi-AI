import io
from pathlib import Path
import pytest
import fitz  # PyMuPDF
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.checklists import generate_dynamic_checklist
from app.api.v1.documents import (
    confirm_extracted_evidence,
    delete_document,
)
from app.database import Base
from app.models.profile import StudentProfile
from app.models.rule import Requirement
from app.models.scholarship import Scholarship
from app.models.source import OfficialSource
from app.schemas.document import EvidenceConfirmationItem, EvidenceConfirmationRequest
from app.services.document_intelligence import (
    DocumentIntelligenceExtractor,
    DocumentParser,
    DynamicChecklistEngine,
)
from app.services.document_service import DocumentService


@pytest.fixture(scope="module")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()

    # Seed official source
    src = OfficialSource(
        id="SRC-TEST-DOCS",
        source_title="Ministry of Education Guidelines",
        issuing_authority="Department of Higher Education",
        official_url="https://scholarships.gov.in/",
    )
    session.add(src)

    # Seed scholarship
    sch = Scholarship(
        id="SCH-TEST-INTELLIGENCE",
        official_name="Central Sector Scheme of Scholarship (CSSS)",
        category="Merit-cum-Means",
        description="Merit scholarship for university students",
        government_department="Department of Higher Education",
        official_source_url="https://scholarships.gov.in/",
        academic_cycle="2024-25",
        verification_date=date(2024, 11, 1),
        course_level="Undergraduate",
        benefit_amount_annual="₹12,000 / year",
        max_annual_income=450000.0,
        min_percentage=80.0,
    )
    session.add(sch)

    # Seed requirements
    req1 = Requirement(
        id="REQ-TEST-INCOME",
        scholarship_id="SCH-TEST-INTELLIGENCE",
        document_type="INCOME_CERTIFICATE",
        title="Annual Family Income Certificate",
        description="Income certificate showing gross income <= ₹4.5L",
        issuing_authority="Revenue Department / Tahsildar",
        is_mandatory=True,
    )
    req2 = Requirement(
        id="REQ-TEST-MARKS",
        scholarship_id="SCH-TEST-INTELLIGENCE",
        document_type="MARKS_CARD",
        title="Class XII Marksheet",
        description="Class XII marksheet showing >= 80% percentile",
        issuing_authority="State Board / CBSE",
        is_mandatory=True,
    )
    req3 = Requirement(
        id="REQ-TEST-BONAFIDE",
        scholarship_id="SCH-TEST-INTELLIGENCE",
        document_type="BONAFIDE_CERTIFICATE",
        title="College Bonafide Certificate",
        description="Bonafide enrollment certificate",
        issuing_authority="College Principal",
        is_mandatory=True,
    )
    session.add_all([req1, req2, req3])

    # Seed student profile
    student = StudentProfile(
        id="STU-TEST-DOCS",
        full_name="Pooja Hegde",
        domicile_state="Karnataka",
        category="General",
        annual_family_income=None,  # Intentionally missing until confirmed from document
        marks_percentage=None,       # Intentionally missing
        current_course="B.Tech Computer Science",
        institution="RV College of Engineering, Bengaluru",
        year_of_study="1st Year",
    )
    session.add(student)
    session.commit()

    yield session
    session.close()


def create_sample_pdf(text_pages: list[str]) -> bytes:
    """Helper to generate an in-memory valid PDF with given text on each page."""
    doc = fitz.open()
    for page_text in text_pages:
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 72), page_text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ============================================================================
# 1. Document Parser & Validation Tests
# ============================================================================

def test_pdf_file_validation_valid():
    """Validates that a genuine PDF passes all structural checks."""
    valid_pdf = create_sample_pdf(["Official Government Certificate\nThis is a valid PDF."])
    # Should not raise
    DocumentParser.validate_file(valid_pdf, "test_document.pdf")
    sha256 = DocumentParser.calculate_sha256(valid_pdf)
    assert len(sha256) == 64


def test_pdf_file_validation_non_pdf():
    """Validates that non-PDF files are rejected."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        DocumentParser.validate_file(b"some content", "image.png")


def test_pdf_file_validation_corrupted_header():
    """Validates that files with invalid PDF headers are rejected."""
    with pytest.raises(ValueError, match="Corrupted or invalid PDF header"):
        DocumentParser.validate_file(b"NOT_A_REAL_PDF_HEADER_CONTENT", "fake.pdf")


def test_pdf_file_validation_oversized():
    """Validates that files exceeding 15MB are rejected."""
    oversized = b"%PDF-" + b"0" * (16 * 1024 * 1024)
    with pytest.raises(ValueError, match="exceeds maximum allowed limit"):
        DocumentParser.validate_file(oversized, "huge.pdf")


def test_pdf_page_tracking_and_metadata():
    """Verifies that multi-page PDFs extract text page-by-page preserving page numbers."""
    multi_page_pdf = create_sample_pdf([
        "Page 1: Government of Karnataka\nDepartment of Revenue",
        "Page 2: Schedule of Assets and Income Verification Details",
        "Page 3: Signature of Tahsildar and Digital Seal",
    ])
    pages_text, ocr_applied, total_pages = DocumentParser.extract_text_and_metadata(
        multi_page_pdf, "multipage.pdf"
    )

    assert total_pages == 3
    assert len(pages_text) == 3
    assert pages_text[0]["page_number"] == 1
    assert "Government of Karnataka" in pages_text[0]["text"]
    assert pages_text[1]["page_number"] == 2
    assert "Schedule of Assets" in pages_text[1]["text"]
    assert pages_text[2]["page_number"] == 3
    assert ocr_applied is False


def test_scanned_pdf_detection_ocr_fallback():
    """Verifies that an image-only scanned page triggers OCR fallback detection."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    # Insert a minimal dummy pixmap image
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 100, 100), 1)
    page.insert_image(page.rect, pixmap=pix)
    # Don't insert text (pure image scan)
    pdf_bytes = doc.tobytes()
    doc.close()

    pages_text, ocr_applied, total_pages = DocumentParser.extract_text_and_metadata(
        pdf_bytes, "scanned_doc.pdf"
    )
    assert total_pages == 1
    assert ocr_applied is True
    assert pages_text[0]["is_scanned"] is True
    assert "SCANNED_DOCUMENT" in pages_text[0]["text"]


# ============================================================================
# 2. Candidate Field Extraction Tests
# ============================================================================

def test_candidate_field_extraction_income_certificate():
    """Verifies candidate field extraction from a realistic Revenue Department Income Certificate."""
    income_cert_text = (
        "GOVERNMENT OF KARNATAKA\n"
        "REVENUE DEPARTMENT - TALUK OFFICE BENGALURU SOUTH\n"
        "ANNUAL INCOME CERTIFICATE\n\n"
        "Certificate No: RD1029384756102\n"
        "Date of Issue: 24/06/2024\n"
        "Candidate Name: Pooja Hegde\n"
        "Father Name: S Hegde\n"
        "Annual Family Income: ₹2,40,000\n"
        "Category: General\n"
        "This certificate is valid for the financial year 2024-25.\n"
    )
    pdf_bytes = create_sample_pdf([income_cert_text])

    pages_text, ocr_applied, total_pages = DocumentParser.extract_text_and_metadata(
        pdf_bytes, "karnataka_income_cert.pdf"
    )
    candidates = DocumentIntelligenceExtractor.extract_candidates_from_pages(pages_text)

    # Verify document type detection
    doc_type = DocumentIntelligenceExtractor.detect_document_type(income_cert_text)
    assert doc_type == "INCOME_CERTIFICATE"

    # Map candidate keys
    cand_dict = {c.field_key: c for c in candidates}

    assert "student_name" in cand_dict
    assert "Pooja Hegde" in cand_dict["student_name"].extracted_value
    assert cand_dict["student_name"].confidence_score >= 0.85
    assert cand_dict["student_name"].page_number == 1

    assert "annual_family_income" in cand_dict
    assert "240,000" in cand_dict["annual_family_income"].extracted_value
    assert cand_dict["annual_family_income"].confidence_score >= 0.90

    assert "certificate_number" in cand_dict
    assert "RD1029384756102" in cand_dict["certificate_number"].extracted_value

    assert "issue_date" in cand_dict
    assert "24/06/2024" in cand_dict["issue_date"].extracted_value


def test_candidate_field_extraction_marks_card():
    """Verifies candidate field extraction from a Class XII / Higher Secondary Marks Card."""
    marks_card_text = (
        "KARNATAKA SCHOOL EXAMINATION AND ASSESSMENT BOARD\n"
        "STATEMENT OF MARKS - CLASS XII / HIGHER SECONDARY EXAMINATION\n\n"
        "Roll No: 2024KRN99128\n"
        "Student Name: Pooja Hegde\n"
        "Institution: National Pre-University College, Bengaluru\n"
        "Course: Class XII Science\n"
        "Academic Year: 2023-24\n"
        "Percentage: 88.50%\n"
        "Result: PASS FIRST CLASS WITH DISTINCTION\n"
    )
    pdf_bytes = create_sample_pdf([marks_card_text])

    pages_text, _, _ = DocumentParser.extract_text_and_metadata(pdf_bytes, "marks_card.pdf")
    candidates = DocumentIntelligenceExtractor.extract_candidates_from_pages(pages_text)

    doc_type = DocumentIntelligenceExtractor.detect_document_type(marks_card_text)
    assert doc_type == "MARKS_CARD"

    cand_dict = {c.field_key: c for c in candidates}
    assert "student_name" in cand_dict
    assert "marks_percentage" in cand_dict
    assert "88.50%" in cand_dict["marks_percentage"].extracted_value
    assert "institution" in cand_dict
    assert "National Pre-University College" in cand_dict["institution"].extracted_value
    assert "academic_year" in cand_dict
    assert "2023-24" in cand_dict["academic_year"].extracted_value


def test_missing_fields_graceful_handling():
    """Verifies that documents with partial information extract available candidates
    without raising errors and never invent missing fields.
    """
    partial_text = (
        "STUDY AND ENROLLMENT CERTIFICATE\n"
        "This is to certify that student is studying B.Tech Computer Science.\n"
        "College: RV College of Engineering\n"
    )
    pdf_bytes = create_sample_pdf([partial_text])
    pages_text, _, _ = DocumentParser.extract_text_and_metadata(pdf_bytes, "partial.pdf")
    candidates = DocumentIntelligenceExtractor.extract_candidates_from_pages(pages_text)

    cand_dict = {c.field_key: c for c in candidates}
    assert "course" in cand_dict or "institution" in cand_dict
    # Crucially, income and marks must NOT be invented
    assert "annual_family_income" not in cand_dict
    assert "marks_percentage" not in cand_dict


def test_non_authenticity_disclaimer():
    """Verifies that non-authenticity legal disclaimer is always attached."""
    disclaimer = DocumentIntelligenceExtractor.DISCLAIMER
    assert "does not verify document authenticity" in disclaimer
    assert "Official validation requires" in disclaimer


# ============================================================================
# 3. Evidence Confirmation & Storage Separation Tests
# ============================================================================

def test_document_processing_and_unconfirmed_evidence_storage(db_session):
    """Verifies end-to-end PDF processing, saving to storage, and storing unconfirmed candidates."""
    doc_service = DocumentService(db_session)
    pdf_text = (
        "GOVERNMENT OF KARNATAKA - REVENUE DEPARTMENT\n"
        "ANNUAL INCOME CERTIFICATE\n"
        "Candidate Name: Pooja Hegde\n"
        "Annual Family Income: ₹2,40,000\n"
        "Certificate No: RD8877665544332\n"
    )
    pdf_bytes = create_sample_pdf([pdf_text])

    res = doc_service.process_and_upload_document(
        file_bytes=pdf_bytes,
        original_filename="income_cert_test.pdf",
        student_profile_id="STU-TEST-DOCS",
    )

    assert res.document.id
    assert res.document.page_count == 1
    assert res.detected_document_type == "INCOME_CERTIFICATE"
    assert len(res.extracted_candidates) >= 2

    # Verify unconfirmed status initially
    for cand in res.extracted_candidates:
        assert cand.is_confirmed is False
        assert cand.confirmed_value is None
        assert cand.raw_text_snippet is not None
        assert cand.page_number == 1


def test_evidence_confirmation_stores_confirmed_separately(db_session):
    """Verifies that confirming an evidence item stores confirmed_value separately from extracted_value."""
    doc_service = DocumentService(db_session)
    pdf_text = (
        "ANNUAL INCOME CERTIFICATE\n"
        "Candidate Name: Pooja Hegde\n"
        "Annual Family Income: ₹2,40,000\n"
    )
    pdf_bytes = create_sample_pdf([pdf_text])
    res = doc_service.process_and_upload_document(
        file_bytes=pdf_bytes,
        original_filename="income_cert_confirm.pdf",
        student_profile_id="STU-TEST-DOCS",
    )

    doc_id = res.document.id
    evidence_list = doc_service.get_evidence_for_document(doc_id)
    income_ev = next(e for e in evidence_list if e.field_key == "annual_family_income")

    # User confirms the extracted value with an exact clean correction
    confirmations = [
        EvidenceConfirmationItem(
            evidence_id=income_ev.id,
            confirmed_value="240000.00",
            is_confirmed=True,
        )
    ]

    updated = doc_service.confirm_evidence_values(doc_id, confirmations)
    assert len(updated) == 1
    assert updated[0].is_confirmed is True
    assert updated[0].confirmed_value == "240000.00"
    # Extracted value must be preserved as original evidence
    assert "240,000" in updated[0].extracted_value


# ============================================================================
# 4. Dynamic Checklist & Eligibility Recalculation Tests
# ============================================================================

def test_dynamic_checklist_generation(db_session):
    """Verifies personalized dynamic checklist generation with verified requirements."""
    engine = DynamicChecklistEngine(db_session)
    checklist = engine.generate_checklist(
        student_profile_id="STU-TEST-DOCS",
        scholarship_id="SCH-TEST-INTELLIGENCE",
    )

    assert checklist.id
    assert checklist.scholarship_id == "SCH-TEST-INTELLIGENCE"
    assert len(checklist.checklist_items) == 3

    # All requirements start as REQUIRED
    for item in checklist.checklist_items:
        assert item["status"] in ("REQUIRED", "NOT_STARTED")
        assert item["is_mandatory"] is True

    # Readiness score must start at 0%
    assert checklist.readiness_score == 0.0
    assert checklist.overall_status in ("REQUIRED", "IN_PROGRESS")


def test_checklist_progression_upon_evidence_confirmation(db_session):
    """Verifies that uploading a document and confirming evidence transitions item
    from REQUIRED -> CONFIRMED and updates readiness score proportionally.
    """
    engine = DynamicChecklistEngine(db_session)
    doc_service = DocumentService(db_session)

    # 1. Generate clean checklist
    checklist = engine.generate_checklist(
        student_profile_id="STU-TEST-DOCS",
        scholarship_id="SCH-TEST-INTELLIGENCE",
    )

    # 2. Upload Income Certificate
    pdf_text = "ANNUAL INCOME CERTIFICATE\nCandidate Name: Pooja Hegde\nAnnual Family Income: ₹2,40,000\n"
    pdf_bytes = create_sample_pdf([pdf_text])
    upload_res = doc_service.process_and_upload_document(
        file_bytes=pdf_bytes,
        original_filename="income_cert.pdf",
        student_profile_id="STU-TEST-DOCS",
    )

    income_ev = next(e for e in upload_res.extracted_candidates if e.field_key == "annual_family_income")

    # 3. Confirm Income Evidence
    updated_chk = engine.confirm_evidence_and_update(
        checklist_id=checklist.id,
        document_id=upload_res.document.id,
        confirmations=[{
            "evidence_id": income_ev.id,
            "confirmed_value": "240000",
            "is_confirmed": True,
        }],
    )

    # 4. Verify Checklist State
    items = updated_chk.checklist_items
    income_item = next(i for i in items if i["document_type"] == "INCOME_CERTIFICATE")
    assert income_item["status"] == "CONFIRMED"
    assert income_item["document_id"] == upload_res.document.id
    assert "annual_family_income" in income_item["confirmed_evidence"]

    # Readiness score should increase from 0 to 33.3% (1 out of 3 confirmed)
    assert updated_chk.readiness_score == pytest.approx(33.3, abs=0.5)
    assert updated_chk.overall_status == "IN_PROGRESS"

    # Crucially, unresolved items must remain REQUIRED
    marks_item = next(i for i in items if i["document_type"] == "MARKS_CARD")
    assert marks_item["status"] == "REQUIRED"


def test_safety_rule_no_premature_submission_ready(db_session):
    """CRITICAL SAFETY TEST:
    Verifies that the system NEVER marks an application ready while required conditions remain unresolved,
    and uploading a document does NOT guarantee eligibility.
    """
    engine = DynamicChecklistEngine(db_session)
    checklist = engine.generate_checklist(
        student_profile_id="STU-TEST-DOCS",
        scholarship_id="SCH-TEST-INTELLIGENCE",
    )

    # Confirm only 1 of 3 items
    items = list(checklist.checklist_items)
    items[0]["status"] = "CONFIRMED"
    score, overall = engine._calculate_readiness(items)

    assert score < 100.0
    assert overall != "READY_FOR_SUBMISSION"
    assert overall == "IN_PROGRESS"


def test_document_deletion_and_checklist_rollback(db_session):
    """Verifies that deleting an uploaded document safely removes physical file,
    deletes DB evidence, and rolls back linked checklist items to REQUIRED.
    """
    doc_service = DocumentService(db_session)
    engine = DynamicChecklistEngine(db_session)

    # 1. Upload Document
    pdf_text = "STATEMENT OF MARKS\nStudent Name: Pooja Hegde\nPercentage: 88.50%\n"
    pdf_bytes = create_sample_pdf([pdf_text])
    upload_res = doc_service.process_and_upload_document(
        file_bytes=pdf_bytes,
        original_filename="marks_to_delete.pdf",
        student_profile_id="STU-TEST-DOCS",
    )
    doc_id = upload_res.document.id
    marks_ev = next(e for e in upload_res.extracted_candidates if e.field_key == "marks_percentage")

    # 2. Link & Confirm on Checklist
    checklist = engine.generate_checklist(
        student_profile_id="STU-TEST-DOCS",
        scholarship_id="SCH-TEST-INTELLIGENCE",
    )
    engine.confirm_evidence_and_update(
        checklist_id=checklist.id,
        document_id=doc_id,
        confirmations=[{"evidence_id": marks_ev.id, "confirmed_value": "88.5", "is_confirmed": True}],
    )

    # 3. Delete Document
    del_result = doc_service.delete_document(doc_id)
    assert del_result["status"] == "DELETED"

    # 4. Verify Checklist Rollback
    reloaded_chk = engine.checklist_repo.get_by_id(checklist.id)
    marks_item = next(i for i in reloaded_chk.checklist_items if i["document_type"] == "MARKS_CARD")
    assert marks_item["status"] in ("REQUIRED", "NOT_STARTED")
    assert marks_item["document_id"] is None
    assert marks_item["confirmed_evidence"] is None


# ============================================================================
# 5. API Endpoints Integration Test
# ============================================================================

def test_api_checklist_and_confirmation_endpoints(db_session):
    """Tests checklist generation and confirmation via API router handlers."""
    # 1. Test generate checklist endpoint
    chk_resp = generate_dynamic_checklist(
        student_profile_id="STU-TEST-DOCS",
        scholarship_id="SCH-TEST-INTELLIGENCE",
        db=db_session,
    )
    assert chk_resp.id
    assert len(chk_resp.checklist_items) == 3
    assert chk_resp.disclaimer is not None

from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.schemas.checklist import ApplicationChecklistCreate, ChecklistItem
from app.schemas.document import ExtractedEvidenceCreate, UploadedDocumentCreate
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate
from app.services.checklist_service import ChecklistService
from app.services.document_service import DocumentService
from app.services.chat_service import ChatService

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


def test_document_and_extracted_evidence_lifecycle(db_session):
    doc_service = DocumentService(db_session)

    # 1. Register Uploaded Document
    doc = doc_service.create_document_record(
        UploadedDocumentCreate(
            id="DOC-INCOME-2025-001",
            document_type="INCOME_CERTIFICATE",
            original_filename="income_cert_ananya.pdf",
            storage_path="/secure/uploads/income_cert_ananya.pdf",
            file_size_bytes=1048576,
            mime_type="application/pdf",
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
    )
    assert doc.id == "DOC-INCOME-2025-001"
    assert doc.processing_status == "PENDING"

    # 2. Add Extracted Evidence
    evidence1 = doc_service.add_extracted_evidence(
        ExtractedEvidenceCreate(
            document_id=doc.id,
            evidence_type="CERT_NUMBER",
            extracted_value="RD00384729104",
            confidence_score=0.98,
            page_number=1,
            raw_text_snippet="Certificate Number: RD00384729104 issued under Nadakacheri portal",
        )
    )
    assert evidence1.extracted_value == "RD00384729104"

    evidence2 = doc_service.add_extracted_evidence(
        ExtractedEvidenceCreate(
            document_id=doc.id,
            evidence_type="ANNUAL_INCOME",
            extracted_value="180000",
            confidence_score=0.95,
            page_number=1,
            raw_text_snippet="Total annual family income assessed is Rs. 1,80,000/-",
        )
    )
    assert evidence2.extracted_value == "180000"

    # 3. Retrieve Document with Evidence
    detailed_doc = doc_service.get_document(doc.id)
    assert len(detailed_doc.extracted_evidence) == 2


def test_application_checklist_generation(db_session):
    checklist_service = ChecklistService(db_session)

    checklist = checklist_service.create_checklist(
        ApplicationChecklistCreate(
            id="CHK-2025-SSP-001",
            student_profile_id="STU-001",
            scholarship_id="SCH-SSP-POSTMATRIC-SCST",
            readiness_score=80.0,
            overall_status="IN_PROGRESS",
            checklist_items=[
                ChecklistItem(
                    name="Income Certificate",
                    status="ready",
                    issuing_office="Tahsildar / Nadakacheri",
                    critical_notes="Valid till 2026",
                ),
                ChecklistItem(
                    name="Caste Certificate",
                    status="ready",
                    issuing_office="Revenue Department",
                ),
                ChecklistItem(
                    name="Bonafide Certificate",
                    status="missing",
                    issuing_office="College Registrar",
                    critical_notes="Current academic year stamp required",
                ),
            ],
        )
    )
    assert checklist.id == "CHK-2025-SSP-001"
    assert checklist.readiness_score == 80.0
    assert len(checklist.checklist_items) == 3


def test_chat_session_and_messages(db_session):
    chat_service = ChatService(db_session)

    session = chat_service.create_session(
        ChatSessionCreate(
            title="Karnataka SSP Post-Matric Query",
            language="kn",
            context_metadata={"scholarship_id": "SCH-SSP-POSTMATRIC-SCST"},
        )
    )
    assert session.id is not None
    assert session.language == "kn"

    # User message
    msg1 = chat_service.add_message(
        session.id,
        ChatMessageCreate(
            sender="user",
            content="ನಾನು ಒಬಿಸಿ ವಿದ್ಯಾರ್ಥಿ, ನನ್ನ ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ 1.8 ಲಕ್ಷ, ನನಗೆ ಸ್ಕಾಲರ್‌ಶಿಪ್ ಸಿಗುತ್ತದೆಯೇ?",
            language="kn",
        ),
    )
    assert msg1.sender == "user"

    # Assistant response with grounded citation
    msg2 = chat_service.add_message(
        session.id,
        ChatMessageCreate(
            sender="assistant",
            content="ಹೌದು, ಕರ್ನಾಟಕ ಪೋಸ್ಟ್-ಮೆಟ್ರಿಕ್ ಮಾರ್ಗಸೂಚಿಗಳ ಪ್ರಕಾರ ನೀವು ಅರ್ಹರಾಗಿದ್ದೀರಿ.",
            language="kn",
            citations=[
                {
                    "title": "SSP Post-Matric Karnataka Official Guidelines",
                    "clause_number": "Section 3.2",
                    "official_source_url": "https://ssp.postmatric.karnataka.gov.in",
                }
            ],
            suggested_follow_ups=["ದಾಖಲೆಗಳ ಪಟ್ಟಿ ತಿಳಿಸಿ", "ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಕೊನೆಯ ದಿನಾಂಕ ಯಾವಾಗ?"],
        ),
    )
    assert msg2.sender == "assistant"
    assert len(msg2.citations) == 1

    fetched_session = chat_service.get_session(session.id)
    assert len(fetched_session.messages) == 2

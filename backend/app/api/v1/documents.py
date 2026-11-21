from typing import Any, Dict, List, Optional
import anyio
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.document import (
    DocumentIntelligenceResponse,
    EvidenceConfirmationRequest,
    ExtractedEvidenceCreate,
    ExtractedEvidenceResponse,
    UploadedDocumentCreate,
    UploadedDocumentResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents & Extracted Evidence"])


@router.post("/upload", response_model=DocumentIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_process_document(
    file: UploadFile = File(...),
    document_type_hint: Optional[str] = Form(None),
    student_profile_id: Optional[str] = Form(None),
    citizen_profile_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Uploads a PDF document, validates integrity, performs page tracking and text extraction,
    extracts candidate fields, and stores unconfirmed evidence candidates.
    """
    service = DocumentService(db)
    try:
        content = await file.read()
        return await anyio.to_thread.run_sync(
            lambda: service.process_and_upload_document(
                file_bytes=content,
                original_filename=file.filename or "uploaded_document.pdf",
                document_type_hint=document_type_hint,
                student_profile_id=student_profile_id,
                citizen_profile_id=citizen_profile_id,
                user_id=user_id,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document parsing failed: {str(e)}",
        )


@router.post("/{doc_id}/confirm-evidence", response_model=List[ExtractedEvidenceResponse])
def confirm_extracted_evidence(
    doc_id: str,
    payload: EvidenceConfirmationRequest,
    checklist_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """User confirms or corrects extracted evidence fields.
    Stores confirmed values separately from unconfirmed extractions.
    If checklist_id is provided, updates checklist status and recalculates eligibility.
    """
    service = DocumentService(db)
    return service.confirm_evidence_values(
        doc_id=doc_id,
        confirmations=payload.items,
        checklist_id=checklist_id,
    )


@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Deletes uploaded document and physical storage file, removing associated evidence
    and dynamically rolling back any linked checklist items.
    """
    service = DocumentService(db)
    return service.delete_document(doc_id)


@router.post("", response_model=UploadedDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document_record(data: UploadedDocumentCreate, db: Session = Depends(get_db)):
    service = DocumentService(db)
    return service.create_document_record(data)


@router.get("/{doc_id}", response_model=UploadedDocumentResponse)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    service = DocumentService(db)
    return service.get_document(doc_id)


@router.get("/user/{user_id}", response_model=List[UploadedDocumentResponse])
def list_user_documents(user_id: str, db: Session = Depends(get_db)):
    service = DocumentService(db)
    return service.list_documents_for_user(user_id)


@router.get("/student/{student_id}", response_model=List[UploadedDocumentResponse])
def list_student_documents(student_id: str, db: Session = Depends(get_db)):
    service = DocumentService(db)
    return service.list_documents_for_student(student_id)


@router.get("/citizen/{citizen_id}", response_model=List[UploadedDocumentResponse])
def list_citizen_documents(citizen_id: str, db: Session = Depends(get_db)):
    service = DocumentService(db)
    return service.list_documents_for_citizen(citizen_id)


@router.post("/evidence", response_model=ExtractedEvidenceResponse, status_code=status.HTTP_201_CREATED)
def add_extracted_evidence(data: ExtractedEvidenceCreate, db: Session = Depends(get_db)):
    service = DocumentService(db)
    return service.add_extracted_evidence(data)


@router.get("/{doc_id}/evidence", response_model=List[ExtractedEvidenceResponse])
def get_document_evidence(doc_id: str, db: Session = Depends(get_db)):
    service = DocumentService(db)
    return service.get_evidence_for_document(doc_id)

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.document import (
    ExtractedEvidenceCreate,
    ExtractedEvidenceResponse,
    UploadedDocumentCreate,
    UploadedDocumentResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents & Extracted Evidence"])


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

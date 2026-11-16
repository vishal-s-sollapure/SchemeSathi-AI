import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    RAGQueryRequest,
)
from app.services.chat_service import ChatService
from app.services.document_intelligence.parser import DocumentParser
from app.services.rag import RAGPipeline, RAGResponse

router = APIRouter(prefix="/chat", tags=["Consultation & Grounded RAG"])


# ============================================================================
# RAG Query & Consultation Endpoints
# ============================================================================

@router.post("/query", response_model=RAGResponse, status_code=status.HTTP_200_OK)
def ask_policy_or_scheme_question(data: RAGQueryRequest, db: Session = Depends(get_db)):
    """Consultation endpoint answering citizen questions grounded exclusively in official government orders.
    
    Guarantees:
    - Zero invented eligibility conditions.
    - Preserves statutory clauses (e.g. PM-KISAN Clause 5, Sakala 7-day e-Attestation).
    - Detects insufficient evidence and answers with factual fallback.
    - Validates all citations against retrieved evidence chunks.
    - Supports English, Kannada, and Hindi.
    """
    pipeline = RAGPipeline.get_instance()
    response = pipeline.ask(
        query=data.query,
        language=data.language,
        scheme_filter=data.scheme_filter,
    )

    # If session_id provided, persist message history
    if data.session_id:
        try:
            service = ChatService(db)
            service.add_message(
                data.session_id,
                ChatMessageCreate(
                    sender="user",
                    content=data.query,
                    language=response.language,
                ),
            )
            service.add_message(
                data.session_id,
                ChatMessageCreate(
                    sender="assistant",
                    content=response.answer,
                    language=response.language,
                    citations=[c.model_dump() for c in response.citations],
                    suggested_follow_ups=response.suggested_follow_ups,
                ),
            )
        except Exception:
            # Continue even if session persistence fails
            pass

    return response


@router.post("/ingest-pdf", status_code=status.HTTP_201_CREATED)
async def ingest_official_pdf(
    file: UploadFile = File(...),
    document_title: str = Form(...),
    government_department: str = Form(...),
    official_source_url: str = Form(...),
    scheme_id: Optional[str] = Form(None),
    applicable_cycle: str = Form("2024-25"),
):
    """Uploads and ingests an authoritative official government PDF using PyMuPDF.
    
    Extracts text page-by-page, generates section-aware chunks, and indexes into the hybrid retriever.
    """
    pipeline = RAGPipeline.get_instance()
    filename = file.filename or "official_document.pdf"

    content = await file.read()
    try:
        DocumentParser.validate_file(content, filename)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        chunks_added = pipeline.ingest_pdf(
            pdf_path=tmp_path,
            document_title=document_title,
            government_department=government_department,
            official_source_url=official_source_url,
            scheme_id=scheme_id,
            applicable_cycle=applicable_cycle,
        )
    finally:
        if tmp_path.exists():
            os.remove(tmp_path)

    return {
        "status": "success",
        "document_title": document_title,
        "filename": filename,
        "evidence_chunks_indexed": chunks_added,
        "verification_status": "VERIFIED",
    }


# ============================================================================
# Chat Session Management Endpoints
# ============================================================================

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(data: ChatSessionCreate, db: Session = Depends(get_db)):
    service = ChatService(db)
    return service.create_session(data)


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    service = ChatService(db)
    return service.get_session(session_id)


@router.get("/users/{user_id}/sessions", response_model=List[ChatSessionResponse])
def list_user_sessions(user_id: str, db: Session = Depends(get_db)):
    service = ChatService(db)
    return service.list_user_sessions(user_id)


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def add_message(session_id: str, data: ChatMessageCreate, db: Session = Depends(get_db)):
    service = ChatService(db)
    return service.add_message(session_id, data)


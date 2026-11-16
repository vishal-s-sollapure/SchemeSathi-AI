import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from app.schemas.policy import (
    PolicyDocumentSummary,
    PolicyExplanationRequest,
    PolicyExplanationResponse,
    PolicySimplificationResult,
)
from app.services.document_intelligence.parser import DocumentParser
from app.services.policy_service import PolicyService

router = APIRouter(prefix="/policy", tags=["Policy and Rights Explainer"])


@router.get("/documents", response_model=List[PolicyDocumentSummary], status_code=status.HTTP_200_OK)
def list_policy_documents(
    search: Optional[str] = Query(None, description="Search across titles, departments, or notification numbers")
):
    """Retrieves verified government circulars, gazette orders, and administrative guidelines."""
    service = PolicyService.get_instance()
    return service.list_policy_documents(search_query=search)


@router.get("/documents/{document_id}", status_code=status.HTTP_200_OK)
def get_policy_document_detail(document_id: str):
    """Retrieves comprehensive structured details and official clauses for a specific policy."""
    service = PolicyService.get_instance()
    doc = service.get_policy_document_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy circular '{document_id}' not found in verified knowledge base."
        )
    return doc


@router.get("/simplify/{document_id}", response_model=PolicySimplificationResult, status_code=status.HTTP_200_OK)
def simplify_policy_document(
    document_id: str,
    language: str = Query("en", description="Output language: en, kn, or hi")
):
    """Generates the 6-part civic simplification workflow for a verified government document.
    
    Includes:
    1. Five-line plain-language summary.
    2. Important conditions and eligibility rules.
    3. Critical dates and statutory filing deadlines.
    4. Required documentary evidence & issuing authorities.
    5. Ordered application steps for citizens.
    6. Important warnings, penalties, and exclusion criteria.
    """
    service = PolicyService.get_instance()
    try:
        return service.simplify_policy(document_id=document_id, language=language)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/explain", response_model=PolicyExplanationResponse, status_code=status.HTTP_200_OK)
def explain_policy_or_clause(request: PolicyExplanationRequest):
    """Answers citizen questions regarding specific circular sections, clauses, and rights.
    
    Adheres strictly to legal safety guardrails:
    - Verbatim official clause retrieval.
    - Plain-language simplification in English, Kannada, or Hindi.
    - Explicit factual fallback when the document does not contain the answer.
    - Never fabricates citizen entitlements or authoritative legal conclusions.
    - Always attaches prominent educational legal disclaimers.
    """
    service = PolicyService.get_instance()
    return service.explain_policy_query(request)


@router.post("/simplify-pdf", response_model=PolicySimplificationResult, status_code=status.HTTP_201_CREATED)
async def simplify_uploaded_government_pdf(
    file: UploadFile = File(...),
    document_title: str = Form(...),
    issuing_department: str = Form("Government Department"),
    official_gazette_url: str = Form("https://india.gov.in"),
    language: str = Form("en"),
):
    """Uploads a citizen/official government PDF and parses it using PyMuPDF into the 6-part simplification workflow."""
    service = PolicyService.get_instance()
    filename = file.filename or "uploaded_circular.pdf"

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
        return service.simplify_uploaded_pdf(
            pdf_path=tmp_path,
            document_title=document_title,
            issuing_department=issuing_department,
            official_gazette_url=official_gazette_url,
            language=language,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process government PDF: {str(e)}"
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

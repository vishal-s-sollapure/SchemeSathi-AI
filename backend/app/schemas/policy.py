from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.chat import ValidatedCitation


class PolicyClauseItem(BaseModel):
    """Specific official clause or section within an authoritative government notification."""
    clause_number: str = Field(..., description="e.g. 'Section 7.3' or 'Clause 5(b)'")
    clause_title: str
    official_text: str = Field(..., description="Verbatim legal statutory phrasing")
    simplified_meaning: Optional[str] = Field(None, description="Plain-language explanation without legal jargon")


class PolicyDeadlineItem(BaseModel):
    """Statutory or administrative timeframe established by the government document."""
    label: str
    timeframe_or_date: str
    statutory_authority: str
    is_critical: bool = False


class PolicyDocumentRequiredItem(BaseModel):
    """Required documentary evidence mandated by the government circular."""
    name: str
    issuing_authority: str
    format_or_requirement: str


class PolicyDocumentSummary(BaseModel):
    """Authoritative government policy, circular, or guideline document metadata."""
    id: str
    title: str
    issuing_department: str
    notification_number: Optional[str] = None
    publication_date: Optional[str] = None
    official_gazette_url: str
    applicable_cycle: str
    category: str = "Government Circular / Guideline"
    executive_summary: str
    clause_count: int = 0
    verification_status: str = "OFFICIALLY_VERIFIED"

    model_config = ConfigDict(from_attributes=True)


class PolicySimplificationResult(BaseModel):
    """Complete 6-part civic policy simplification workflow."""
    document_id: str
    document_title: str
    issuing_department: str
    notification_number: Optional[str] = None
    publication_date: Optional[str] = None
    official_gazette_url: str
    applicable_cycle: str
    language: str = "en"

    # Core 6 Simplification Workflow Pillars
    five_line_summary: List[str] = Field(..., description="Exactly five plain-language bullet points")
    important_conditions: List[str] = Field(..., description="Eligibility criteria, restrictions, and qualifications")
    dates_and_deadlines: List[PolicyDeadlineItem] = Field(..., description="Key statutory timelines and calendar deadlines")
    required_documents: List[PolicyDocumentRequiredItem] = Field(..., description="Required proofs and certifying authorities")
    application_steps: List[str] = Field(..., description="Sequential steps for citizens to apply or comply")
    important_warnings: List[str] = Field(..., description="Penalties, disqualifications, and statutory exclusion cautions")

    # Ambiguities & Statutory Safety Disclaimers
    flagged_ambiguities: List[str] = Field(default_factory=list, description="Unclear edge cases in the circular")
    legal_disclaimer: str = (
        "Legal Notice & Guardrail: This plain-language explanation is an educational, simplified aid "
        "grounded strictly in official government circulars. It does not constitute formal legal representation "
        "or authoritative administrative adjudication. For binding statutory proceedings, always consult "
        "the official gazette notification and designated departmental nodal officers."
    )

    model_config = ConfigDict(from_attributes=True)


class PolicyExplanationRequest(BaseModel):
    """Citizen query regarding a specific government document, section, or clause."""
    document_id: Optional[str] = Field(None, description="Identifier of the verified government circular")
    clause_or_section: Optional[str] = Field(None, description="Optional specific clause reference, e.g. 'Clause 5(b)'")
    question: str = Field(..., min_length=2, max_length=1000, description="Citizen inquiry in natural language")
    language: str = Field("en", max_length=10, description="en, kn, or hi")

    model_config = ConfigDict(extra="ignore")


class PolicySupportingPassage(BaseModel):
    """Authoritative passage retrieved directly from the verified gazette or guidelines."""
    source_title: str
    clause_or_section: str
    page_number: Optional[str] = None
    official_text: str
    official_source_url: str
    issuing_department: str


class PolicyExplanationResponse(BaseModel):
    """Civic explanation grounded in official passages with explicit legal guardrails."""
    question: str
    document_id: Optional[str] = None
    document_title: Optional[str] = None
    language: str = "en"
    simplified_explanation: str
    clause_referenced: Optional[str] = None
    verbatim_official_clause: Optional[str] = None
    supporting_passages: List[PolicySupportingPassage] = Field(default_factory=list)
    citations: List[ValidatedCitation] = Field(default_factory=list)
    sufficient_evidence: bool = True
    important_dates: List[str] = Field(default_factory=list)
    restrictions_and_responsibilities: List[str] = Field(default_factory=list)
    suggested_follow_ups: List[str] = Field(default_factory=list)
    legal_disclaimer: str = (
        "Legal Guardrail: This simplified explanation is provided for educational and civic informational "
        "purposes. It does not constitute formal legal advice or binding judicial interpretation. "
        "If a requirement is omitted from official records, no citizen right is implied or assumed."
    )

    model_config = ConfigDict(from_attributes=True)

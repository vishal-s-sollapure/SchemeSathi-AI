from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CitationModel(BaseModel):
    id: Optional[str] = None
    title: str
    document_name: Optional[str] = None
    issuing_authority: Optional[str] = None
    circular_number: Optional[str] = None
    notification_date: Optional[str] = None
    clause_number: Optional[str] = None
    excerpt: str
    official_source_url: str
    verification_badge: Optional[str] = "Official Verified Source"


class ValidatedCitation(BaseModel):
    """Citation verified to originate strictly from retrieved official evidence."""
    source_title: str
    circular_number: Optional[str] = None
    clause_or_section: str
    page_number: Optional[str] = None
    official_source_url: str
    verification_status: str = "OFFICIALLY_VERIFIED"
    matched_chunk_id: str
    excerpt: str


class ChatMessageBase(BaseModel):
    sender: str = Field(..., description="user or assistant")
    content: str
    language: str = Field("en", max_length=10)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_follow_ups: List[str] = Field(default_factory=list)


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: str
    session_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionBase(BaseModel):
    title: str = Field("Civic Consultation", max_length=255)
    language: str = Field("en", max_length=10)
    context_metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatSessionCreate(ChatSessionBase):
    id: Optional[str] = None
    user_id: Optional[str] = None


class ChatSessionResponse(ChatSessionBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RAGQueryRequest(BaseModel):
    """Citizen consultation query for source-grounded RAG retrieval and citation."""
    query: str = Field(..., min_length=2, max_length=1500, description="Question about scheme, scholarship, or rights")
    session_id: Optional[str] = Field(None, description="Optional active chat session to persist conversation")
    language: Optional[str] = Field(None, max_length=10, description="en, kn, or hi")
    scheme_filter: Optional[str] = Field(None, description="Optional scheme_id filter e.g. SCHEME-PM-KISAN")

    model_config = ConfigDict(extra="ignore")


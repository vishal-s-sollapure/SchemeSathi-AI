from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True

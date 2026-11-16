from sqlalchemy import Column, ForeignKey, JSON, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class ChatSession(Base, TimestampMixin):
    """User conversation session for multilingual assistance and rights explanation."""
    __tablename__ = "chat_sessions"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), default="Civic Consultation", nullable=False)
    language = Column(String(10), default="en", nullable=False)  # en, kn, hi, te, ta, mr
    context_metadata = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

    def __repr__(self) -> str:
        return f"<ChatSession {self.id}: {self.title} ({self.language})>"


class ChatMessage(Base, TimestampMixin):
    """Individual message within a consultation session with grounded citations."""
    __tablename__ = "chat_messages"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    session_id = Column(String(50), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    citations = Column(JSON, default=list, nullable=False)  # List of citation dicts
    suggested_follow_ups = Column(JSON, default=list, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage {self.id}: {self.sender} ({self.language})>"

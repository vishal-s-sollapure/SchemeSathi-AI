from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.chat import ChatMessage, ChatSession
from app.repositories.chat_repo import ChatRepository
from app.schemas.chat import (
    ChatMessageCreate,
    ChatSessionCreate,
)


class ChatService:
    def __init__(self, db: Session):
        self.repo = ChatRepository(db)

    def get_session(self, session_id: str) -> ChatSession:
        session = self.repo.get_with_messages(session_id)
        if not session:
            raise EntityNotFoundException("ChatSession", session_id)
        return session

    def list_user_sessions(self, user_id: str) -> List[ChatSession]:
        return self.repo.get_by_user(user_id)

    def create_session(self, data: ChatSessionCreate) -> ChatSession:
        session = ChatSession(
            id=data.id,
            user_id=data.user_id,
            title=data.title,
            language=data.language,
            context_metadata=data.context_metadata,
        )
        return self.repo.create(session)

    def add_message(self, session_id: str, data: ChatMessageCreate) -> ChatMessage:
        self.get_session(session_id)
        message = ChatMessage(
            session_id=session_id,
            sender=data.sender,
            content=data.content,
            language=data.language,
            citations=data.citations,
            suggested_follow_ups=data.suggested_follow_ups,
        )
        return self.repo.add_message(message)

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.chat import ChatMessage, ChatSession
from app.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatSession]):
    def __init__(self, db: Session):
        super().__init__(ChatSession, db)

    def get_with_messages(self, session_id: str) -> Optional[ChatSession]:
        return (
            self.db.query(ChatSession)
            .options(joinedload(ChatSession.messages))
            .filter(ChatSession.id == session_id)
            .first()
        )

    def get_by_user(self, user_id: str) -> List[ChatSession]:
        return self.db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

    def add_message(self, message: ChatMessage) -> ChatMessage:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

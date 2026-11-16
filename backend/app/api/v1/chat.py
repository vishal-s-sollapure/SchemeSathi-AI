from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Consultation & Chat"])


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

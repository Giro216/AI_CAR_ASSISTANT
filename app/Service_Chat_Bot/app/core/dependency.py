import os
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositoriy.conversation_repository_protocol import ConversationRepository
from app.repositoriy.sql_conversation_repository import SqlConversationRepository
from app.service.chatService import ChatService

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_conversation_repository(db: Session = Depends(get_db)) -> ConversationRepository:
    return SqlConversationRepository(db)

def get_chat_service(
    repo: ConversationRepository = Depends(get_conversation_repository)
) -> ChatService:
    return ChatService(repository=repo)
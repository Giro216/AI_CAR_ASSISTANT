import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ChatMessageIn(BaseModel):
	message: str = Field(..., min_length=1, max_length=2000, description="Текст сообщения")
	conversation_id: str = Field(..., description="Обязательный UUID диалога, генерируемый фронтендом")
	user_id: Optional[str] = Field(None, description="Передается фронтендом только для гостей")

class ChatMessageOut(BaseModel):
	reply: str
	conversation_id: str

class ConversationOut(BaseModel):
	id: str
	summary: Optional[str] = None
	created_at: datetime
	updated_at: datetime

	class Config:
		from_attributes = True

class HistoryMessageOut(BaseModel):
	role: str
	content: str
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class ChatMessageIn(BaseModel):
	message: str
	conversation_id: Optional[str] = None

class ChatMessageOut(BaseModel):
	reply: str
	conversation_id: Optional[str] = None

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
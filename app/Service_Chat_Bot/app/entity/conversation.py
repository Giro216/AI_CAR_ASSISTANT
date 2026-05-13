from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Conversation:
	conversation_id: str
	user_id: str
	summary: str | None
	created_at: datetime
	updated_at: datetime


@dataclass
class Message:
	message_id: str
	conversation_id: str
	role: str
	content: str
	created_at: datetime

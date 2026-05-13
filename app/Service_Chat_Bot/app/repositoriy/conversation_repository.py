from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.model.conversation import Conversation, Message


class InMemoryConversationRepository:
	def __init__(self) -> None:
		self._messages_by_conversation: dict[str, list[Message]] = {}
		self._conversation_by_user: dict[str, str] = {}
		self._conversation_by_id: dict[str, Conversation] = {}
		self._summary_by_conversation: dict[str, str] = {}
		self._summary_cursor_by_conversation: dict[str, int] = {}
		self._hot_limit: int = 7

	# Gets an existing conversation id or creates a new one for the user.
	def get_or_create_conversation_id(self, user_id: str, conversation_id: str | None) -> str:
		if conversation_id:
			return conversation_id
		existing = self._conversation_by_user.get(user_id)
		if existing:
			return existing
		new_id = f"conv_{uuid4().hex}"
		now = datetime.now(timezone.utc)
		self._conversation_by_user[user_id] = new_id
		self._conversation_by_id[new_id] = Conversation(
			conversation_id=new_id,
			user_id=user_id,
			summary=None,
			created_at=now,
			updated_at=now,
		)
		return new_id

	# Stores a new message in memory.
	def add_message(self, conversation_id: str, role: str, content: str) -> None:
		record = Message(
			message_id=f"msg_{uuid4().hex}",
			conversation_id=conversation_id,
			role=role,
			content=content,
			created_at=datetime.now(timezone.utc),
		)
		self._messages_by_conversation.setdefault(conversation_id, []).append(record)
		self._touch_conversation(conversation_id)

	# Returns full message history for the conversation.
	def load_messages(self, conversation_id: str) -> list[dict]:
		records = self._messages_by_conversation.get(conversation_id, [])
		return [{"role": item.role, "content": item.content} for item in records]

	# Builds prompt messages from summary plus hot context.
	def load_prompt_messages(self, conversation_id: str) -> list[dict]:
		summary = self._summary_by_conversation.get(conversation_id)
		cursor = self._summary_cursor_by_conversation.get(conversation_id, 0)
		records = self._messages_by_conversation.get(conversation_id, [])
		hot_context = records[cursor:]
		if len(hot_context) > self._hot_limit:
			hot_context = hot_context[-self._hot_limit:]

		prompt_messages: list[dict] = []
		if summary:
			prompt_messages.append({"role": "system", "content": f"Summary of previous messages: {summary}"})
		prompt_messages.extend({"role": item.role, "content": item.content} for item in hot_context)
		return prompt_messages

	# Returns the current summary text.
	def get_summary(self, conversation_id: str) -> str:
		return self._summary_by_conversation.get(conversation_id, "")

	# Returns the next batch of messages to summarize (size 7).
	def get_next_summary_batch(self, conversation_id: str) -> list[Message] | None:
		records = self._messages_by_conversation.get(conversation_id, [])
		cursor = self._summary_cursor_by_conversation.get(conversation_id, 0)
		if len(records) - cursor <= self._hot_limit:
			return None
		batch_end = cursor + self._hot_limit
		return records[cursor:batch_end]

	# Advances summary pointer and stores the new summary text.
	def advance_summary(self, conversation_id: str, summary: str, batch_size: int) -> None:
		cursor = self._summary_cursor_by_conversation.get(conversation_id, 0)
		self._summary_by_conversation[conversation_id] = summary
		self._summary_cursor_by_conversation[conversation_id] = cursor + batch_size
		self._touch_conversation(conversation_id, summary)

	# Updates timestamps and summary on the Conversation model.
	def _touch_conversation(self, conversation_id: str, summary: str | None = None) -> None:
		conversation = self._conversation_by_id.get(conversation_id)
		if not conversation:
			return
		if summary is not None:
			conversation.summary = summary
		conversation.updated_at = datetime.now(timezone.utc)

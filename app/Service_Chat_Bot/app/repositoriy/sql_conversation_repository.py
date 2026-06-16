from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func, select, update, delete
from sqlalchemy.orm import Session

from app.entity.conversation import Message
from app.models.conversation_models import ConversationModel, MessageModel

class SqlConversationRepository:
	def __init__(self, session: Session) -> None:
		self._session = session
		self._hot_limit: int = 7

	def get_or_create_conversation_id(self, user_id: str, conversation_id: str) -> str:
		conversation = self._session.execute(
			select(ConversationModel).where(ConversationModel.id == conversation_id)
		).scalar_one_or_none()

		# Сценарий А: Диалога с таким ID еще нет -> создаем его для текущего пользователя
		if conversation is None:
			conversation = ConversationModel(
				id=conversation_id,
				user_id=user_id,
				summary=None,
				summary_cursor=0,
			)
			self._session.add(conversation)
			self._session.flush()
			return conversation_id

		# Сценарий Б: Диалог существует, но принадлежит другому пользователю
		if conversation.user_id != user_id:
			raise ValueError("Доступ к чужому диалогу запрещен.")

		# Сценарий В: Диалог существует и принадлежит текущему пользователю -> возвращаем его
		return conversation_id

	def add_message(self, conversation_id: str, role: str, content: str) -> None:
		message = MessageModel(
			id=str(uuid4()),
			conversation_id=conversation_id,
			role=role,
			content=content,
			created_at=datetime.now(timezone.utc),
		)
		self._session.add(message)
		self._session.execute(
			update(ConversationModel)
			.where(ConversationModel.id == conversation_id)
			.values(updated_at=datetime.now(timezone.utc))
		)
		self._session.flush()

	def load_messages(self, conversation_id: str) -> list[dict]:
		rows = self._session.execute(
			select(MessageModel)
			.where(MessageModel.conversation_id == conversation_id)
			.order_by(MessageModel.created_at.asc(), MessageModel.id.asc())
		).scalars().all()
		return [{"role": item.role, "content": item.content} for item in rows]

	def load_prompt_messages(self, conversation_id: str) -> list[dict]:
		conversation = self._session.execute(
			select(ConversationModel)
			.where(ConversationModel.id == conversation_id)
		).scalar_one_or_none()
		if conversation is None:
			return []

		total_count = self._session.execute(
			select(func.count(MessageModel.id))
			.where(MessageModel.conversation_id == conversation_id)
		).scalar_one()
		cursor = conversation.summary_cursor or 0

		if total_count - cursor <= self._hot_limit:
			offset = cursor
			limit = total_count - cursor
		else:
			offset = max(total_count - self._hot_limit, 0)
			limit = self._hot_limit

		rows = self._session.execute(
			select(MessageModel)
			.where(MessageModel.conversation_id == conversation_id)
			.order_by(MessageModel.created_at.asc(), MessageModel.id.asc())
			.offset(offset)
			.limit(limit)
		).scalars().all()

		prompt_messages: list[dict] = []
		if conversation.summary:
			prompt_messages.append(
				{"role": "system", "content": f"Summary of previous messages: {conversation.summary}"}
			)
		prompt_messages.extend({"role": item.role, "content": item.content} for item in rows)
		return prompt_messages

	def get_summary(self, conversation_id: str) -> str:
		summary = self._session.execute(
			select(ConversationModel.summary)
			.where(ConversationModel.id == conversation_id)
		).scalar_one_or_none()
		return summary or ""

	def get_next_summary_batch(self, conversation_id: str) -> list[Message] | None:
		conversation = self._session.execute(
			select(ConversationModel)
			.where(ConversationModel.id == conversation_id)
		).scalar_one_or_none()
		if conversation is None:
			return None

		total_count = self._session.execute(
			select(func.count(MessageModel.id))
			.where(MessageModel.conversation_id == conversation_id)
		).scalar_one()
		cursor = conversation.summary_cursor or 0
		if total_count - cursor <= self._hot_limit:
			return None

		rows = self._session.execute(
			select(MessageModel)
			.where(MessageModel.conversation_id == conversation_id)
			.order_by(MessageModel.created_at.asc(), MessageModel.id.asc())
			.offset(cursor)
			.limit(self._hot_limit)
		).scalars().all()

		return [
			Message(
				message_id=item.id,
				conversation_id=item.conversation_id,
				role=item.role,
				content=item.content,
				created_at=item.created_at,
			)
			for item in rows
		]

	def advance_summary(self, conversation_id: str, summary: str, batch_size: int) -> None:
		conversation = self._session.execute(
			select(ConversationModel)
			.where(ConversationModel.id == conversation_id)
		).scalar_one_or_none()
		if conversation is None:
			return
		new_cursor = (conversation.summary_cursor or 0) + batch_size
		self._session.execute(
			update(ConversationModel)
			.where(ConversationModel.id == conversation_id)
			.values(
				summary=summary,
				summary_cursor=new_cursor,
				updated_at=datetime.now(timezone.utc),
			)
		)
		self._session.flush()

	def list_conversations(self, user_id: str) -> List[ConversationModel]:
		stmt = select(ConversationModel).where(ConversationModel.user_id == user_id).order_by(ConversationModel.updated_at.desc())
		return list(self._session.execute(stmt).scalars().all())

	def get_conversation(self, conversation_id: str) -> Optional[ConversationModel]:
		stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
		return self._session.execute(stmt).scalar_one_or_none()

	def delete_conversation(self, conversation_id: str) -> None:
		stmt = delete(ConversationModel).where(ConversationModel.id == conversation_id)
		self._session.execute(stmt)
		self._session.flush()

	def count_messages(self, conversation_id: str) -> int:
		stmt = select(func.count(MessageModel.id)).where(MessageModel.conversation_id == conversation_id)
		return self._session.execute(stmt).scalar() or 0
	
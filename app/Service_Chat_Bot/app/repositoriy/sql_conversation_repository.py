from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.entity.conversation import Message
from app.models.conversation_models import ConversationModel, MessageModel


class SqlConversationRepository:
	def __init__(self, session_factory=SessionLocal) -> None:
		self._session_factory = session_factory
		self._hot_limit: int = 7

	# Opens a new SQLAlchemy session for repository operations.
	@contextmanager
	def _session_scope(self) -> Session:
		session = self._session_factory()
		try:
			yield session
			session.commit()
		except Exception:
			session.rollback()
			raise
		finally:
			session.close()

	# Gets an existing conversation id or creates a new one for the user.
	def get_or_create_conversation_id(self, user_id: str, conversation_id: str | None) -> str:
		with self._session_scope() as session:
			if conversation_id:
				conversation = session.execute(
					select(ConversationModel).where(ConversationModel.id == conversation_id)
				).scalar_one_or_none()
				if conversation is None:
					conversation = ConversationModel(
						id=conversation_id,
						user_id=user_id,
						summary=None,
						summary_cursor=0,
					)
					session.add(conversation)
				return conversation_id

			conversation = session.execute(
				select(ConversationModel)
				.where(ConversationModel.user_id == user_id)
				.order_by(ConversationModel.updated_at.desc())
			).scalar_one_or_none()
			if conversation:
				return conversation.id

			new_id = str(uuid4())
			conversation = ConversationModel(
				id=new_id,
				user_id=user_id,
				summary=None,
				summary_cursor=0,
			)
			session.add(conversation)
			return new_id

	# Stores a new message in SQL.
	def add_message(self, conversation_id: str, role: str, content: str) -> None:
		with self._session_scope() as session:
			message = MessageModel(
				id=str(uuid4()),
				conversation_id=conversation_id,
				role=role,
				content=content,
				created_at=datetime.now(timezone.utc),
			)
			session.add(message)
			session.execute(
				update(ConversationModel)
				.where(ConversationModel.id == conversation_id)
				.values(updated_at=datetime.now(timezone.utc))
			)

	# Returns full message history for the conversation.
	def load_messages(self, conversation_id: str) -> list[dict]:
		with self._session_scope() as session:
			rows = session.execute(
				select(MessageModel)
				.where(MessageModel.conversation_id == conversation_id)
				.order_by(MessageModel.created_at.asc(), MessageModel.id.asc())
			).scalars().all()
			return [{"role": item.role, "content": item.content} for item in rows]

	# Builds prompt messages from summary plus hot context.
	def load_prompt_messages(self, conversation_id: str) -> list[dict]:
		with self._session_scope() as session:
			conversation = session.execute(
				select(ConversationModel)
				.where(ConversationModel.id == conversation_id)
			).scalar_one_or_none()
			if conversation is None:
				return []

			total_count = session.execute(
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

			rows = session.execute(
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

	# Returns the current summary text.
	def get_summary(self, conversation_id: str) -> str:
		with self._session_scope() as session:
			summary = session.execute(
				select(ConversationModel.summary)
				.where(ConversationModel.id == conversation_id)
			).scalar_one_or_none()
			return summary or ""

	# Returns the next batch of messages to summarize (size 7).
	def get_next_summary_batch(self, conversation_id: str) -> list[Message] | None:
		with self._session_scope() as session:
			conversation = session.execute(
				select(ConversationModel)
				.where(ConversationModel.id == conversation_id)
			).scalar_one_or_none()
			if conversation is None:
				return None

			total_count = session.execute(
				select(func.count(MessageModel.id))
				.where(MessageModel.conversation_id == conversation_id)
			).scalar_one()
			cursor = conversation.summary_cursor or 0
			if total_count - cursor <= self._hot_limit:
				return None

			rows = session.execute(
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

	# Advances summary pointer and stores the new summary text.
	def advance_summary(self, conversation_id: str, summary: str, batch_size: int) -> None:
		with self._session_scope() as session:
			conversation = session.execute(
				select(ConversationModel)
				.where(ConversationModel.id == conversation_id)
			).scalar_one_or_none()
			if conversation is None:
				return
			new_cursor = (conversation.summary_cursor or 0) + batch_size
			session.execute(
				update(ConversationModel)
				.where(ConversationModel.id == conversation_id)
				.values(
					summary=summary,
					summary_cursor=new_cursor,
					updated_at=datetime.now(timezone.utc),
				)
			)

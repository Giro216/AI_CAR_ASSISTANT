from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ConversationModel(Base):
	__tablename__ = "conversations"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	user_id: Mapped[str] = mapped_column(String(128), index=True)
	summary: Mapped[str | None] = mapped_column(Text, nullable=True)
	summary_cursor: Mapped[int] = mapped_column(Integer, default=0)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		onupdate=func.now(),
	)

	messages: Mapped[list["MessageModel"]] = relationship(
		"MessageModel",
		back_populates="conversation",
		cascade="all, delete-orphan",
	)


class MessageModel(Base):
	__tablename__ = "messages"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	conversation_id: Mapped[str] = mapped_column(
		String(36),
		ForeignKey("conversations.id", ondelete="CASCADE"),
		index=True,
	)
	role: Mapped[str] = mapped_column(String(32))
	content: Mapped[str] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

	conversation: Mapped[ConversationModel] = relationship("ConversationModel", back_populates="messages")

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Profile(Base):
	__tablename__ = "user_profiles"

	# Первичным ключом является UUID пользователя, пришедший из Auth Service
	user_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		nullable=False
	)
	first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
	last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
	phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
	city: Mapped[str | None] = mapped_column(String(100), nullable=True)

	# TODO Криво заполняются preferences если меняется набор передаваемых значений
	# JSONB поле для любых динамически меняющихся предпочтений и метаданных
	preferences: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		default=lambda: datetime.now(timezone.utc),
		onupdate=lambda: datetime.now(timezone.utc),
		nullable=False
	)
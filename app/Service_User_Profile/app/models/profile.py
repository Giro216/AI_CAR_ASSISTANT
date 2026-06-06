import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Profile(Base):
	__tablename__ = "user_profiles"

	user_id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		nullable=False
	)
	first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
	last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
	city: Mapped[str | None] = mapped_column(String(100), nullable=True)
	age: Mapped[int | None] = mapped_column(Integer, nullable=True)
	children_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

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
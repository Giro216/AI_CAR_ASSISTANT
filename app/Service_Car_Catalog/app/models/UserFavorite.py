from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.config.database import Base


class UserFavorite(Base):
	__tablename__ = "user_favorites"

	user_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
	car_id = Column(String(100), primary_key=True, nullable=False)

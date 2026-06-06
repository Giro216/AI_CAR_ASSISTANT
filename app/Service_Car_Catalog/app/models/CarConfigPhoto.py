from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint, func

from app.config.database import Base


class CarConfigPhoto(Base):
	__tablename__ = "car_config_photos"

	id = Column(Integer, primary_key=True, autoincrement=True)
	config_id = Column(Integer, ForeignKey("car_unique_configs.id", ondelete="CASCADE"), nullable=False)
	url = Column(Text, nullable=False)
	priority = Column(Integer, nullable=False)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)

	__table_args__ = (
		UniqueConstraint("config_id", "url", name="uq_config_photo_url"),
		UniqueConstraint("config_id", "priority", name="uq_config_photo_priority"),
	)

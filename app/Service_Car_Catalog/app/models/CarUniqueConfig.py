from sqlalchemy import Column, Integer, Text, DateTime, UniqueConstraint, func

from app.config.database import Base


class CarUniqueConfig(Base):
	__tablename__ = "car_unique_configs"

	id = Column(Integer, primary_key=True, autoincrement=True)
	brand_model_id = Column(Integer, nullable=False)
	generation = Column(Text, nullable=True)
	series = Column(Text, nullable=True)
	body_type = Column(Text, nullable=True)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)

	__table_args__ = (
		UniqueConstraint("brand_model_id", "generation", "series", "body_type", name="uq_unique_config"),
	)

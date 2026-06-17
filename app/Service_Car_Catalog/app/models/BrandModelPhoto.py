from sqlalchemy import Column, Integer, Text, DateTime, UniqueConstraint, func

from app.config.database import Base


class BrandModelPhoto(Base):
	__tablename__ = "brand_model_photos"

	id = Column(Integer, primary_key=True, autoincrement=True)
	brand_model_id = Column(Integer, nullable=False)
	url = Column(Text, nullable=False)
	priority = Column(Integer, nullable=False)
	created_at = Column(DateTime, server_default=func.now(), nullable=False)

	__table_args__ = (
		UniqueConstraint("brand_model_id", "url", name="uq_brand_model_photo_url"),
		UniqueConstraint("brand_model_id", "priority", name="uq_brand_model_photo_priority"),
	)

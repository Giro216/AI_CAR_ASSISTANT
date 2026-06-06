from typing import Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base
from app.entity.CarModelEntity import CarModelEntity


class CarModelInfo(Base):
	__tablename__ = "unique_models_with_year_range"

	id: Mapped[str] = mapped_column(String, primary_key=True)
	brand_model_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
	make: Mapped[str] = mapped_column(String)
	model: Mapped[str] = mapped_column(String)
	start_year: Mapped[int] = mapped_column(Integer)
	end_year: Mapped[int] = mapped_column(Integer)

	@property
	def to_entity(self) -> CarModelEntity:
		return CarModelEntity(
			id=self.id,
			brand_model_id=self.brand_model_id,
			brand=self.make,
			model=self.model,
			start_year=self.start_year,
			end_year=self.end_year,
		)

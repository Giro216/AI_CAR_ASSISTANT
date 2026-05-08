from typing import Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base
from app.entity.CarGenEntity import CarGenEntity


class CarModelGenInfo(Base):
    __tablename__ = "cars_main_info_view"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    brand_model_id: Mapped[Optional[str]] = mapped_column(String)
    make: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    generation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    series: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    year_from: Mapped[int] = mapped_column(Integer)
    year_to: Mapped[int] = mapped_column(Integer)
    body_type: Mapped[str] = mapped_column(String)

    @property
    def to_entity(self) -> CarGenEntity:
        return CarGenEntity(
            id=str(self.id),
            brand_model_id=self.brand_model_id,
            brand=self.make,
            model=self.model,
            generation=self.generation,
            gen_comment=self.series,
            year_from=self.year_from,
            year_to=self.year_to,
            body_type=self.body_type,
        )

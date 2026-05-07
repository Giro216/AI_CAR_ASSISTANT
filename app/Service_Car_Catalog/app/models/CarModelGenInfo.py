from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base
from app.entity.CarGenEntity import CarGenEntity


class CarModelGenInfo(Base):
    __tablename__ = "cars_main_info_view"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    make: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    generation: Mapped[str] = mapped_column(String)
    series: Mapped[str] = mapped_column(String)
    year_from: Mapped[int] = mapped_column(Integer)
    year_to: Mapped[int] = mapped_column(Integer)
    body_type: Mapped[str] = mapped_column(String)

    @property
    def to_entity(self) -> CarGenEntity:
        return CarGenEntity(
            id=str(self.id),
            brand=self.make,
            model=self.model,
            generation=self.generation,
            gen_comment=self.series,
            year_from=self.year_from,
            year_to=self.year_to,
            body_type=self.body_type,
        )

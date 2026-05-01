from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base
from app.entity.CarEntity import CarEntity


class CarModel(Base):
    __tablename__ = "cars_main_info_view"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    make: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    year_from: Mapped[int] = mapped_column(Integer)
    year_to: Mapped[int] = mapped_column(Integer)
    body_type: Mapped[str] = mapped_column(String)
    engine_type: Mapped[str] = mapped_column(String)
    transmission_type: Mapped[str] = mapped_column(String)

    @property
    def to_entity(self) -> CarEntity:
        return CarEntity(
            id=self.id,
            brand=self.make,
            model=self.model,
            year_from=self.year_from,
            year_to=self.year_to,
            body_type=self.body_type,
            fuel=self.engine_type,
            transmission=self.transmission_type,
        )

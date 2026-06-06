from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class FiltersModel(Base):
	__tablename__ = "all_filters_metadata"

	id: Mapped[str] = mapped_column(String, primary_key=True)
	make: Mapped[str] = mapped_column(String)
	model: Mapped[str] = mapped_column(String)
	body_type: Mapped[str] = mapped_column(String)
	engine_type: Mapped[str] = mapped_column(String)
	transmission_type: Mapped[str] = mapped_column(String)

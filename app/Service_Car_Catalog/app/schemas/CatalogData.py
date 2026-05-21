from __future__ import annotations

from pydantic import BaseModel

from app.schemas.CarModelCard import CarModelCard


class CatalogData(BaseModel):
	cars_count: int
	founded_cars: list[CarModelCard]

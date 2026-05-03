from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.image import ImageResponse


class CarBasicInfo(BaseModel):
    id: str = Field(..., description="Идентификатор автомобиля")
    brand: str
    model: str
    price: Optional[int] = Field(default=None, description="Цена (пока заглушка)")
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    fuel: Optional[str] = None
    enginePower: Optional[str] = None
    transmission: Optional[str] = None
    bodyType: Optional[str] = None
    imageUrl: Optional[str] = None
    imageMeta: Optional[ImageResponse] = None

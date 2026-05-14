from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.schemas.image import ImageResponse


class CarModelCard(BaseModel):
    id: str
    brand_model_id: Optional[str] = None
    brand: str
    model: str
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    imageUrl: Optional[str] = None
    imageMeta: Optional[ImageResponse] = None
    isPopular: bool = False

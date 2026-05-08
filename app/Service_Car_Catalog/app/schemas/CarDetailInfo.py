from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.schemas.image import ImageResponse


class CarDetailInfo(BaseModel):
    """Подробная карточка — пока минимальный набор полей (можно расширять без ломки API)."""
    id: str
    brand_model_id: Optional[str] = None
    brand: str
    model: str
    imageUrl: Optional[str] = None
    imageMeta: Optional[ImageResponse] = None

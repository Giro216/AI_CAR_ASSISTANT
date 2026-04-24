# Импортируем классы из библиотеки Pydantic для создания моделей данных и валидации
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.image import ImageResponse


class CarsCatalogRequest(BaseModel):
    make_name: str = Field(..., max_length=127)
    model_name: str = Field(..., max_length=127)


class Car(BaseModel):
    id: str = Field(..., description="Идентификатор автомобиля")
    brand: str
    model: str
    price: Optional[int] = Field(default=None, description="Цена (пока заглушка)")
    year: Optional[int] = None
    mileage: Optional[int] = None
    engine: Optional[str] = None
    transmission: Optional[str] = None
    fuel: Optional[str] = None
    bodyType: Optional[str] = None
    imageUrl: Optional[str] = None
    imageMeta: Optional[ImageResponse] = None
    isPopular: bool = False


class CarDetail(BaseModel):
    """Подробная карточка — пока минимальный набор полей (можно расширять без ломки API)."""

    id: str
    brand: str
    model: str
    imageUrl: Optional[str] = None
    imageMeta: Optional[ImageResponse] = None


class FiltersMeta(BaseModel):
    bodyTypes: List[str] = Field(default_factory=list)
    fuels: List[str] = Field(default_factory=list)
    transmissions: List[str] = Field(default_factory=list)
    brands: List[str] = Field(default_factory=list)

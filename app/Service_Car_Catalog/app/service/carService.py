from __future__ import annotations

import asyncio
from typing import List, Optional

from fastapi import HTTPException

from app.entity.CarEntity import CarEntity
from app.repository.cars_repository import CarsRepository
from app.schemas.image import ImageResponse
from app.schemas.schemas import Car, CarDetail, FiltersMeta
from app.service.imageService import ImageService


class CarService:
    """Application Service (use-cases слой).

    - не зависит от FastAPI роутеров
    - зависит от абстракций репозитория и сервиса изображений
    """

    def __init__(self, repo: CarsRepository, image_service: ImageService) -> None:
        self._repo = repo
        self._image_service = image_service

        # чтобы не спамить внешнее API, ограничиваем параллелизм
        self._image_sem = asyncio.Semaphore(5)

    async def _image_for(self, brand: str, model: str) -> Optional[ImageResponse]:
        query = f"{brand} {model} car"
        async with self._image_sem:
            return await self._image_service.get_image(query)

    async def _to_car(self, e: CarEntity) -> Car:
        image = await self._image_for(e.brand, e.model)
        return Car(
            id=e.id,
            brand=e.brand,
            model=e.model,
            year=e.year,
            bodyType=e.body_type,
            fuel=e.fuel,
            transmission=e.transmission,
            imageUrl=image.imageUrl if image else None,
            imageMeta=image,
            # остальное пока заглушки
            price=None,
            mileage=None,
            engine=None,
            isPopular=False,
        )

    async def get_cars(self, *, brand: Optional[str] = None, model: Optional[str] = None, sort: Optional[str] = None) -> \
            List[Car]:
        items = self._repo.list(brand=brand, model=model, sort=sort)
        return list(await asyncio.gather(*[self._to_car(e) for e in items]))

    async def get_popular_cars(self, *, limit: int = 10) -> List[Car]:
        items = self._repo.popular(limit=limit)
        cars = list(await asyncio.gather(*[self._to_car(e) for e in items]))
        return [c.model_copy(update={"isPopular": True}) for c in cars]

    async def search(self, *, q: str, limit: int = 20) -> List[Car]:
        items = self._repo.search(q, limit=limit)
        return list(await asyncio.gather(*[self._to_car(e) for e in items]))

    async def get_filters_meta(self) -> FiltersMeta:
        items = self._repo.list()
        body_types = sorted({c.body_type for c in items if c.body_type})
        fuels = sorted({c.fuel for c in items if c.fuel})
        transmissions = sorted({c.transmission for c in items if c.transmission})
        brands = sorted({c.brand for c in items if c.brand})
        return FiltersMeta(bodyTypes=body_types, fuels=fuels, transmissions=transmissions, brands=brands)

    async def get_car_detail(self, *, car_id: str) -> CarDetail:
        e = self._repo.get_by_id(car_id)
        if not e:
            raise HTTPException(status_code=404, detail="Car not found")
        image = await self._image_for(e.brand, e.model)
        return CarDetail(
            id=e.id,
            brand=e.brand,
            model=e.model,
            imageUrl=image.imageUrl if image else None,
            imageMeta=image,
        )

    async def get_similar_cars(self, *, car_id: str, limit: int = 10) -> List[Car]:
        items = self._repo.similar(car_id, limit=limit)
        return list(await asyncio.gather(*[self._to_car(e) for e in items]))

    async def get_car_pricing(self, *, car_id: str):
        # Заглушка на будущее. Формат можно согласовать позже.
        e = self._repo.get_by_id(car_id)
        if not e:
            raise HTTPException(status_code=404, detail="Car not found")
        return {"carId": car_id, "currentPrice": None, "history": []}

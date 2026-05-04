from __future__ import annotations

import asyncio
import os
from typing import List, Optional

from fastapi import HTTPException

from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity
from app.repository.CarsRepository import CarsRepository
from app.schemas import CarBasicInfo, CarDetailInfo, FiltersMeta
from app.schemas.CarModelCard import CarModelCard
from app.schemas.image import ImageResponse
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
        parse_images = os.getenv("PARSE_IMAGES")
        if parse_images == '0':
            return None
        query = f"{brand} {model} car"
        async with self._image_sem:
            return await self._image_service.get_image(query)

    async def _to_car_basic_info(self, e: CarGenEntity) -> CarBasicInfo:
        image = await self._image_for(e.brand, e.model)
        return CarBasicInfo(
            id=str(e.id),
            brand=e.brand,
            model=e.model,
            year_from=e.year_from,
            year_to=e.year_to,
            bodyType=e.body_type,
            fuel=e.fuel,
            transmission=e.transmission,
            imageUrl=image.imageUrl if image else None,
            imageMeta=image,
            # остальное пока заглушки
            price=None,
            enginePower=None,
        )

    async def _to_car_model_card(self, e: CarModelEntity) -> CarModelCard:
        image = await self._image_for(e.brand, e.model)
        return CarModelCard(
            id=str(e.id),
            brand=e.brand,
            model=e.model,
            start_year=e.start_year,
            end_year=e.end_year,
            imageUrl=image.imageUrl if image else None,
            imageMeta=image,
        )

    async def get_models(self, *, brand: Optional[str] = None, model: Optional[str] = None,
                         sort: Optional[str] = None, limit: int = 50, page: int = 1) -> \
            List[CarModelCard]:
        offset = (page - 1) * limit
        items = self._repo.list_models(brand=brand, model=model, sort=sort, limit=limit, offset=offset)
        return list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))

    async def get_popular_cars(self, *, limit: int = 10) -> List[CarModelCard]:
        items = self._repo.popular(limit=limit)
        cars = list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))
        return [c.model_copy(update={"isPopular": True}) for c in cars]

    async def search(self, *, q: str, limit: int = 20) -> List[CarModelCard]:
        items = self._repo.search_models(q, limit=limit)
        return list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))

    async def get_filters_meta(self) -> FiltersMeta:
        items = self._repo.list_gens()
        body_types = sorted({c.body_type for c in items if c.body_type})
        fuels = sorted({c.fuel for c in items if c.fuel})
        transmissions = sorted({c.transmission for c in items if c.transmission})
        brands = sorted({c.brand for c in items if c.brand})
        models = sorted({c.model for c in items if c.model})
        return FiltersMeta(bodyTypes=body_types, fuels=fuels, transmissions=transmissions, brands=brands, models=models)

    async def get_car_detail(self, *, car_id: str) -> CarDetailInfo:
        e = self._repo.get_by_id(car_id)
        if not e:
            raise HTTPException(status_code=404, detail="Car not found")
        image = await self._image_for(e.brand, e.model)
        return CarDetailInfo(
            id=str(e.id),
            brand=e.brand,
            model=e.model,
            imageUrl=image.imageUrl if image else None,
            imageMeta=image,
        )

    async def get_similar_cars(self, *, car_id: str, limit: int = 10) -> List[CarModelCard]:
        items = self._repo.similar(car_id, limit=limit)
        return list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))

    async def get_car_pricing(self, *, car_id: str):
        # Заглушка на будущее. Формат можно согласовать позже.
        e = self._repo.get_by_id(car_id)
        if not e:
            raise HTTPException(status_code=404, detail="Car not found")
        return {"carId": car_id, "currentPrice": None, "history": []}

    async def get_models_generations(self) -> List[CarBasicInfo]:
        pass

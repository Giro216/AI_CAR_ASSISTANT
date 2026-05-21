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
from app.schemas.CatalogData import CatalogData
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
			brand_model_id=e.brand_model_id,
			brand=e.brand,
			model=e.model,
			generation=e.generation,
			gen_comment=e.gen_comment,
			year_from=e.year_from,
			year_to=e.year_to,
			bodyType=e.body_type,
			imageUrl=image.imageUrl if image else None,
			imageMeta=image,
		)

	async def _to_car_model_card(self, e: CarModelEntity) -> CarModelCard:
		image = await self._image_for(e.brand, e.model)
		return CarModelCard(
			id=str(e.id),
			brand_model_id=str(e.brand_model_id),
			brand=e.brand,
			model=e.model,
			start_year=e.start_year,
			end_year=e.end_year,
			imageUrl=image.imageUrl if image else None,
			imageMeta=image,
		)

	async def get_models(self, *, brand_model_id: Optional[str] = None, brand: Optional[str] = None,
	                     model: Optional[str] = None,
	                     sort: Optional[str] = None, limit: int = 50, page: int = 1) -> \
			CatalogData:
		offset = (page - 1) * limit
		items = self._repo.list_models(brand_model_id=brand_model_id, brand=brand, model=model, sort=sort, limit=limit,
		                               offset=offset)
		total = self._repo.count_models(brand_model_id=brand_model_id, brand=brand, model=model)
		founded_cars: List[CarModelCard] = list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))

		return CatalogData(cars_count=total, founded_cars=founded_cars)

	async def get_popular_cars(self, *, limit: int = 10) -> List[CarModelCard]:
		items = self._repo.popular(limit=limit)
		cars = list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))
		return [c.model_copy(update={"isPopular": True}) for c in cars]

	async def search(self, *, q: str, limit: int = 20) -> List[CarModelCard]:
		items = self._repo.search_models(q, limit=limit)
		return list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))

	async def get_filters_meta(self) -> FiltersMeta:
		filters = self._repo.get_filters_meta()
		return FiltersMeta(
			bodyTypes=filters.bodyTypes,
			fuels=filters.fuels,
			transmissions=filters.transmissions,
			brands=filters.brands,
			models=filters.models,
		)

	async def get_car_detail(self, *, brand_model_id: Optional[str] = None, car_id: Optional[str] = None,
	                         body_type: Optional[str] = None) -> CarDetailInfo:
		lookup_id = brand_model_id or car_id
		if not lookup_id:
			raise HTTPException(status_code=400, detail="brand_model_id is required")

		e = self._repo.get_by_brand_model_id(lookup_id, body_type=body_type)
		if not e:
			e = self._repo.get_by_id(lookup_id)
		if not e:
			raise HTTPException(status_code=404, detail="Car not found")
		image = await self._image_for(e.brand, e.model)
		return CarDetailInfo(
			id=str(e.id),
			brand_model_id=e.brand_model_id,
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

	async def get_models_generations(self, *, brand_model_id: str, brand: Optional[str] = None,
	                                 model: Optional[str] = None) -> List[CarBasicInfo]:
		items = self._repo.list_gens(brand_model_id=brand_model_id, brand=brand, model=model)
		return list(await asyncio.gather(*[self._to_car_basic_info(e) for e in items]))

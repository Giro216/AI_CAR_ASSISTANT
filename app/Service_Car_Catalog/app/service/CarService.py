from __future__ import annotations

import asyncio
import os
import uuid
from typing import List, Optional

from fastapi import HTTPException, status

from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity
from app.repository.CarsRepository import CarsRepository
from app.schemas import CarBasicInfo, FiltersMeta, CarFullInfoConfig
from app.schemas.CarModelCard import CarModelCard
from app.schemas.CatalogData import CatalogData
from app.schemas.image import ImageResponse
from app.service.ImageService import ImageService


class CarService:
	"""Application Service (use-cases слой).

	- не зависит от FastAPI роутеров
	- зависит от абстракций репозитория и сервиса изображений
	"""

	def __init__(self, repo: CarsRepository, image_service: ImageService) -> None:
		self._repo = repo
		self._image_service = image_service

		self._image_sem = asyncio.Semaphore(5)

	async def _image_for_model(self, brand_model_id: Optional[str | int], brand: str, model: str) -> Optional[
		ImageResponse]:
		parse_images = os.getenv("PARSE_IMAGES")
		if parse_images == '0':
			return None

		bm_id_int = None
		if brand_model_id is not None:
			if isinstance(brand_model_id, int):
				bm_id_int = brand_model_id
			elif isinstance(brand_model_id, str) and brand_model_id.isdigit():
				bm_id_int = int(brand_model_id)

		# Промпт: make + model + car
		query = f"{brand} {model} car"
		async with self._image_sem:
			# Метод get_image сам проверит и запишет кэш по brand_model_id
			return await self._image_service.get_image(query, brand_model_id=bm_id_int)

	async def _image_for_config(
			self,
			brand_model_id: int,
			make: str,
			model: str,
			generation: str,
			series: str,
			body_type: str
	) -> Optional[ImageResponse]:
		parse_images = os.getenv("PARSE_IMAGES")
		if parse_images == '0':
			return None

		# Получаем или автоматически регистрируем ID уникальной конфигурации
		config_id = self._repo.get_or_create_config_id(
			brand_model_id=brand_model_id,
			generation=generation,
			series=series,
			body_type=body_type
		)

		query_parts = [make, model, generation, series, body_type, "car"]
		query = " ".join([p for p in query_parts if p])

		async with self._image_sem:
			return await self._image_service.get_image(query, config_id=config_id)

	# Вспомогательный метод-заглушка на случай отсутствия brand_model_id
	async def _image_for_fallback(self, brand: str, model: str) -> Optional[ImageResponse]:
		parse_images = os.getenv("PARSE_IMAGES")
		if parse_images == '0':
			return None
		query = f"{brand} {model} car"
		async with self._image_sem:
			return await self._image_service.get_image(query)

	async def _to_car_basic_info(self, e: CarGenEntity) -> CarBasicInfo:
		image = await self._image_for_model(e.brand_model_id, e.brand, e.model)
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
		image = await self._image_for_model(e.brand_model_id, e.brand, e.model)
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

	async def search(self, *, q: str, limit: int = 20) -> CatalogData:
		items = self._repo.search_models(q, limit=limit)
		cars = list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))
		return CatalogData(cars_count=len(cars), founded_cars=cars)

	async def get_filters_meta(self) -> FiltersMeta:
		filters = self._repo.get_filters_meta()
		return FiltersMeta(
			bodyTypes=filters.bodyTypes,
			fuels=filters.fuels,
			transmissions=filters.transmissions,
			brands=filters.brands,
			models=filters.models,
		)

	# --- ЛАКОНИЧНЫЙ МЕТОД КОНФИГУРАТОРА С ПОДДЕРЖКОЙ МНОЖЕСТВЕННЫХ ФОТО ---
	async def get_car_config(self, *, brand_model_id: str, generation: str, body_type: Optional[str] = None) -> List[
		CarFullInfoConfig]:
		items = self._repo.get_full_info(brand_model_id=brand_model_id, generation=generation, body_type=body_type)
		if not items:
			raise HTTPException(status_code=404, detail="Car config not found")

		try:
			bm_id_int = int(brand_model_id)
		except (ValueError, TypeError):
			bm_id_int = 0

		configs_list = []
		for item in items:
			gen = item.generation or ""
			series = item.series or ""
			bt = item.body_type or ""

			# 1. Проверяем кэш в БД car_config_photos на наличие множественных фото
			cached_urls = self._repo.get_config_photos(
				brand_model_id=bm_id_int,
				generation=gen,
				series=series,
				body_type=bt
			)

			if cached_urls:
				image_urls = cached_urls
				# Конструируем метаданные по главной фотографии
				image_meta = ImageResponse(title=f"{item.make} {item.model}", imageUrl=cached_urls[0],
				                           source="DB_Config_Cache")
			else:
				# 2. Если в кэше пусто — запускаем парсинг (он автоматически сохранит до 3 фото с приоритетами в БД)
				image_meta = await self._image_for_config(
					brand_model_id=bm_id_int,
					make=item.make or "",
					model=item.model or "",
					generation=gen,
					series=series,
					body_type=bt
				)

				# 3. Мгновенно вычитываем сохраненные фото из БД, чтобы вернуть массив из 3-х штук на фронтенд
				image_urls = self._repo.get_config_photos(
					brand_model_id=bm_id_int,
					generation=gen,
					series=series,
					body_type=bt
				)

			config_dto = CarFullInfoConfig.model_validate(item)
			config_dto.imageUrl = image_urls if image_urls else []
			config_dto.imageMeta = image_meta
			configs_list.append(config_dto)

		return configs_list

	async def get_similar_cars(self, *, car_id: str, limit: int = 10) -> List[CarModelCard]:
		items = self._repo.similar(car_id, limit=limit)
		return list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))

	async def get_car_pricing(self, *, car_id: str):
		e = self._repo.get_by_id(car_id)
		if not e:
			raise HTTPException(status_code=404, detail="Car not found")
		return {"carId": car_id, "currentPrice": None, "history": []}

	async def get_models_generations(self, *, brand_model_id: str, brand: Optional[str] = None,
	                                 model: Optional[str] = None) -> List[CarBasicInfo]:
		items = self._repo.list_gens(brand_model_id=brand_model_id, brand=brand, model=model)
		return list(await asyncio.gather(*[self._to_car_basic_info(e) for e in items]))

	async def add_to_favorites(self, user_id: uuid.UUID, car_id: str) -> None:
		if not self._repo.model_exists(car_id):
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"Автомобиль с ID {car_id} не найден в каталоге базы данных."
			)

		self._repo.add_favorite(user_id=user_id, car_id=car_id)

	async def remove_from_favorites(self, user_id: uuid.UUID, car_id: str) -> None:
		if not self._repo.model_exists(car_id):
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"Автомобиль с ID {car_id} не найден в каталоге базы данных."
			)

		if not self._repo.favorite_exists(user_id=user_id, car_id=car_id):
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Этот автомобиль отсутствует в вашем списке избранного."
			)

		self._repo.remove_favorite(user_id=user_id, car_id=car_id)

	async def get_favorite_cars(self, user_id: uuid.UUID) -> List[CarModelCard]:
		car_ids = self._repo.list_favorites(user_id)
		if not car_ids:
			return []

		items = self._repo.get_models_by_ids(car_ids)

		return list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))

from __future__ import annotations

import asyncio
import os
import uuid
from typing import List, Optional

import redis
from fastapi import HTTPException, status

from app.config.logger import get_logger
from app.entity.CarGenEntity import CarGenEntity
from app.entity.CarModelEntity import CarModelEntity
from app.repository.CarsRepository import CarsRepository
from app.schemas import CarBasicInfo, FiltersMeta, CarFullInfoConfig
from app.schemas.CarModelCard import CarModelCard
from app.schemas.CatalogData import CatalogData
from app.schemas.image import ImageResponse
from app.service.ImageService import ImageService

logger = get_logger(__name__)


class CarService:
	def __init__(self, repo: CarsRepository, image_service: ImageService,
	             redis_client: Optional[redis.Redis] = None) -> None:
		self._repo = repo
		self._image_service = image_service
		self._redis = redis_client
		self._image_sem = asyncio.Semaphore(15)

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

		logger.info(
			f"Resolving unique config_id from DB for brand_model_id: {brand_model_id}, gen: {generation}, series: {series}")
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

	async def _image_for_fallback(self, brand: str, model: str) -> Optional[ImageResponse]:
		parse_images = os.getenv("PARSE_IMAGES")
		if parse_images == '0':
			return None
		query = f"{brand} {model} car"
		async with self._image_sem:
			return await self._image_service.get_image(query)

	async def _to_car_basic_info(self, e: CarGenEntity) -> CarBasicInfo:
		bm_id_int = None
		if e.brand_model_id is not None:
			if isinstance(e.brand_model_id, int):
				bm_id_int = e.brand_model_id
			elif isinstance(e.brand_model_id, str) and e.brand_model_id.isdigit():
				bm_id_int = int(e.brand_model_id)

		cached_urls = []
		if bm_id_int:
			cached_urls = self._repo.get_brand_model_photos(bm_id_int)

		image = await self._image_for_model(e.brand_model_id, e.brand, e.model)
		display_url = image.thumbnailUrl if image and image.thumbnailUrl else (image.imageUrl if image else None)
		
		image_urls_list = cached_urls if cached_urls else ([display_url] if display_url else [])

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
			imageUrl=display_url,
			imageUrls=image_urls_list,
			imageMeta=image,
		)

	async def _to_car_model_card(self, e: CarModelEntity) -> CarModelCard:
		bm_id_int = None
		if e.brand_model_id is not None:
			if isinstance(e.brand_model_id, int):
				bm_id_int = e.brand_model_id
			elif isinstance(e.brand_model_id, str) and e.brand_model_id.isdigit():
				bm_id_int = int(e.brand_model_id)

		cached_urls = []
		if bm_id_int:
			cached_urls = self._repo.get_brand_model_photos(bm_id_int)

		image = await self._image_for_model(e.brand_model_id, e.brand, e.model)
		display_url = image.thumbnailUrl if image and image.thumbnailUrl else (image.imageUrl if image else None)
		
		image_urls_list = cached_urls if cached_urls else ([display_url] if display_url else [])

		return CarModelCard(
			id=str(e.id),
			brand_model_id=str(e.brand_model_id),
			brand=e.brand,
			model=e.model,
			start_year=e.start_year,
			end_year=e.end_year,
			imageUrl=display_url,
			imageUrls=image_urls_list,
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
		top_ids = []
		if self._redis:
			try:
				logger.info(f"Querying Redis Sorted Set 'cars:popular_views' for top {limit} popular cars")
				top_ids = self._redis.zrevrange("cars:popular_views", 0, limit - 1)
				logger.info(f"Redis returned popular IDs: {top_ids}")
			except Exception as e:
				logger.error(f"Error reading popular set from Redis: {str(e)}", exc_info=True)

		if top_ids:
			logger.info(f"Querying PostgreSQL for model information of popular IDs: {top_ids}")
			items = self._repo.get_models_by_ids(top_ids)
			id_order = {val: idx for idx, val in enumerate(top_ids)}
			items = sorted(items, key=lambda x: id_order.get(str(x.brand_model_id), 999))
		else:
			logger.warning("Redis popular set is empty or offline. Falling back to default DB popular query.")
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

			# Пакетная проверка кэша L1/L2
			logger.info(
				f"Checking cache layers for config photos. brand_model_id: {bm_id_int}, gen: {gen}, series: {series}")
			cached_urls = self._repo.get_config_photos(
				brand_model_id=bm_id_int,
				generation=gen,
				series=series,
				body_type=bt
			)

			if cached_urls:
				logger.info(f"Cache HIT for config photos. Count: {len(cached_urls)}")
				image_urls = cached_urls
				image_meta = ImageResponse(title=f"{item.make} {item.model}", imageUrl=cached_urls[0],
				                           source="DB_Config_Cache")
			else:
				logger.info(f"Cache MISS for config photos. Triggering external parsing.")
				# Запускаем парсинг
				image_meta = await self._image_for_config(
					brand_model_id=bm_id_int,
					make=item.make or "",
					model=item.model or "",
					generation=gen,
					series=series,
					body_type=bt
				)

				# Вычитываем полный массив фото из СУБД для отдачи на фронтенд
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

		# Фиксируем просмотр модели в Redis
		if self._redis and brand_model_id:
			try:
				logger.info(f"Incrementing view count for brand_model_id: {brand_model_id}")
				await self._redis.zincrby("cars:popular_views", 1, str(brand_model_id))
			except Exception as e:
				logger.warning(f"Failed to increment popular score in Redis: {str(e)}")

		return list(await asyncio.gather(*[self._to_car_basic_info(e) for e in items]))

	async def add_to_favorites(self, user_id: uuid.UUID, car_id: str) -> None:
		if not self._repo.model_exists(car_id):
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"Автомобиль с ID {car_id} не найден в каталоге базы данных."
			)

		logger.info(f"Saving car_id: {car_id} to user_id: {user_id} favorites in DB")
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

		logger.info(f"Deleting car_id: {car_id} from user_id: {user_id} favorites in DB")
		self._repo.remove_favorite(user_id=user_id, car_id=car_id)

	async def get_favorite_cars(self, user_id: uuid.UUID) -> List[CarModelCard]:
		logger.info(f"Fetching favorite car list from DB for user_id: {user_id}")
		car_ids = self._repo.list_favorites(user_id)
		if not car_ids:
			return []

		items = self._repo.get_models_by_ids(car_ids)

		return list(await asyncio.gather(*[self._to_car_model_card(e) for e in items]))

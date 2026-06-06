from __future__ import annotations

import base64
import hashlib
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

import aiohttp
import redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.logger import get_logger
from app.schemas.image import ImageResponse

logger = get_logger(__name__)


class ImageService(ABC):
	@abstractmethod
	async def get_image(
			self,
			query: str,
			brand_model_id: Optional[int] = None,
			config_id: Optional[int] = None
	) -> Optional[ImageResponse]:
		"""Вернуть объект изображения по поисковому запросу."""


class SerperImageService(ImageService):
	def __init__(self, *, api_key: Optional[str], db: Optional[Session] = None,
	             redis_client: Optional[redis.Redis] = None, storage_dir: Optional[Path] = None) -> None:
		self._api_key = api_key
		self._db = db
		self._redis = redis_client
		self._IMG_TTL = int(os.getenv("IMG_TTL", "3600"))
		self._cache: Dict[str, Optional[ImageResponse]] = {}
		self._storage_dir = storage_dir or Path.cwd() / "storage" / "images"
		self._storage_dir.mkdir(parents=True, exist_ok=True)

	@staticmethod
	def _parse_data_url(data_url: str) -> tuple[Optional[str], Optional[bytes]]:
		if not data_url.startswith("data:") or ";base64," not in data_url:
			return None, None

		header, encoded = data_url.split(",", 1)
		mime = header.split(";", 1)[0].replace("data:", "")
		ext = "bin"
		if "/" in mime:
			ext = mime.split("/", 1)[1] or "bin"

		try:
			decoded = base64.b64decode(encoded)
		except Exception:
			return None, None

		return ext, decoded

	def _save_embedded_image(self, *, query: str, image_url: str, thumbnail_data_url: str) -> Optional[str]:
		ext, decoded = self._parse_data_url(thumbnail_data_url)
		if not ext or not decoded:
			return None

		file_key = f"{query}|{image_url}|{len(decoded)}"
		file_name = hashlib.sha256(file_key.encode("utf-8")).hexdigest()[:24] + f".{ext}"
		target_path = self._storage_dir / file_name

		if not target_path.exists():
			logger.info(f"Writing embedded binary thumbnail image to disk: {target_path}")
			target_path.write_bytes(decoded)

		return str(target_path)

	async def _save_thumbnail_url(self, *, query: str, image_url: str, thumbnail_url: str) -> Optional[str]:
		save_images = os.getenv("SAVE_IMAGES", "0")
		if save_images != "1":
			return None

		if not thumbnail_url:
			return None

		if thumbnail_url.startswith("data:"):
			return self._save_embedded_image(query=query, image_url=image_url, thumbnail_data_url=thumbnail_url)

		file_key = f"{query}|{image_url}|{thumbnail_url}"
		file_name = hashlib.sha256(file_key.encode("utf-8")).hexdigest()[:24]

		try:
			timeout = aiohttp.ClientTimeout(total=7)
			async with aiohttp.ClientSession(timeout=timeout) as session:
				logger.info(f"Downloading external thumbnail file: {thumbnail_url}")
				async with session.get(thumbnail_url) as resp:
					if resp.status < 200 or resp.status >= 300:
						logger.warning(f"Failed to download thumbnail, HTTP status: {resp.status}")
						return None
					content = await resp.read()
					content_type = resp.headers.get("Content-Type", "")
		except Exception as e:
			logger.error(f"Error downloading thumbnail: {str(e)}", exc_info=True)
			return None

		ext = "bin"
		if "image/" in content_type:
			ext = content_type.split("image/", 1)[1].split(";", 1)[0].strip() or "bin"
		elif "." in thumbnail_url.rsplit("/", 1)[-1]:
			ext = thumbnail_url.rsplit("/", 1)[-1].split(".", 1)[-1].split("?", 1)[0] or "bin"

		target_path = self._storage_dir / f"{file_name}.{ext}"
		if not target_path.exists():
			logger.info(f"Writing parsed thumbnail to local file: {target_path}")
			target_path.write_bytes(content)
		return str(target_path)

	def _get_from_db_cache(
			self,
			brand_model_id: Optional[int],
			config_id: Optional[int],
			query: str
	) -> Optional[ImageResponse]:
		# Быстрая проверка Кэша Redis L1
		if self._redis:
			try:
				if brand_model_id is not None:
					redis_url = self._redis.get(f"car:img:brand_model:{brand_model_id}")
					if redis_url:
						img_resp = ImageResponse(title=query, imageUrl=redis_url, source="REDIS_L1_Brand_Cache")
						self._cache[query] = img_resp
						return img_resp
				elif config_id is not None:
					redis_url = self._redis.get(f"car:img:config:{config_id}")
					if redis_url:
						img_resp = ImageResponse(title=query, imageUrl=redis_url, source="REDIS_L1_Config_Cache")
						self._cache[query] = img_resp
						return img_resp
			except Exception as e:
				logger.warning(f"Failed to read from Redis L1 cache layer: {str(e)}")

		if not self._db:
			return None

		cached_url = None
		source_label = ""

		if brand_model_id is not None:
			from app.models.BrandModelPhoto import BrandModelPhoto
			stmt = select(BrandModelPhoto.url).where(
				BrandModelPhoto.brand_model_id == brand_model_id
			).order_by(BrandModelPhoto.priority.asc())
			cached_url = self._db.execute(stmt).scalars().first()
			source_label = "DB_Postgres_Brand_Cache"

			# Записываем в Redis L1 для ускорения последующих запросов
			if cached_url and self._redis:
				try:
					self._redis.setex(f"car:img:brand_model:{brand_model_id}", self._IMG_TTL, cached_url)
				except Exception as e:
					logger.warning(f"Failed to write DB value back to Redis L1 cache: {str(e)}")

		elif config_id is not None:
			from app.models.CarConfigPhoto import CarConfigPhoto
			logger.info(f"Redis L1 MISS. Checking PostgreSQL L2 cache for config_id: {config_id}")
			stmt = select(CarConfigPhoto.url).where(
				CarConfigPhoto.config_id == config_id
			).order_by(CarConfigPhoto.priority.asc())
			cached_url = self._db.execute(stmt).scalars().first()
			source_label = "DB_Postgres_Config_Cache"

			# Записываем в Redis L1
			if cached_url and self._redis:
				try:
					self._redis.setex(f"car:img:config:{config_id}", self._IMG_TTL, cached_url)
				except Exception as e:
					logger.warning(f"Failed to write DB value back to Redis L1 cache: {str(e)}")

		if cached_url:
			logger.info(f"PostgreSQL HIT. Found cached for brand_model_id: {brand_model_id}")
			img_resp = ImageResponse(
				title=query,
				imageUrl=cached_url,
				source=source_label
			)
			self._cache[query] = img_resp
			return img_resp

		return None

	def _save_to_db_cache(self, brand_model_id: Optional[int], config_id: Optional[int], url: str,
	                      priority: int) -> None:
		# Физическая запись в кэш Redis L1
		if self._redis and priority == 1:
			try:
				if brand_model_id is not None:
					logger.info(f"Saving photo to Redis L1 cache for brand_model_id: {brand_model_id}")
					self._redis.setex(f"car:img:brand_model:{brand_model_id}", 86400, url)
				elif config_id is not None:
					logger.info(f"Saving photo to Redis L1 cache for config_id: {config_id}")
					self._redis.setex(f"car:img:config:{config_id}", 86400, url)
			except Exception as e:
				logger.warning(f"Failed to write parsed image back to Redis L1 cache: {str(e)}")

		if not self._db:
			return

		# Физическая запись в СУБД PostgreSQL
		try:
			if brand_model_id is not None:
				from app.models.BrandModelPhoto import BrandModelPhoto
				exists = self._db.query(BrandModelPhoto).filter_by(
					brand_model_id=brand_model_id,
					url=url
				).first()
				if not exists:
					p_exists = self._db.query(BrandModelPhoto).filter_by(
						brand_model_id=brand_model_id,
						priority=priority
					).first()
					if not p_exists:
						logger.info(
							f"Writing photo to PostgreSQL. brand_model_id: {brand_model_id}, priority: {priority}")
						photo = BrandModelPhoto(brand_model_id=brand_model_id, url=url, priority=priority)
						self._db.add(photo)
						self._db.commit()

			elif config_id is not None:
				from app.models.CarConfigPhoto import CarConfigPhoto
				exists = self._db.query(CarConfigPhoto).filter_by(
					config_id=config_id,
					url=url
				).first()
				if not exists:
					p_exists = self._db.query(CarConfigPhoto).filter_by(
						config_id=config_id,
						priority=priority
					).first()
					if not p_exists:
						logger.info(f"Writing photo to PostgreSQL L2. config_id: {config_id}, priority: {priority}")
						photo = CarConfigPhoto(config_id=config_id, url=url, priority=priority)
						self._db.add(photo)
						self._db.commit()
		except Exception as e:
			logger.error(f"Error writing parsed photo back to PostgreSQL L2 cache database: {str(e)}", exc_info=True)

	async def _fetch_from_serper(self, query: str) -> Optional[dict]:
		url = "https://google.serper.dev/images"
		payload = {
			"q": query,
			"gl": "ru",
			"hl": "ru",
			"num": 3,
		}
		headers = {
			"X-API-KEY": self._api_key,
			"Content-Type": "application/json",
		}

		timeout = aiohttp.ClientTimeout(total=7)
		async with aiohttp.ClientSession(timeout=timeout) as session:
			logger.info(f"Cache MISS. Sending HTTP request to Google Serper API. Query: '{query}'")
			async with session.post(url, json=payload, headers=headers) as resp:
				if resp.status < 200 or resp.status >= 300:
					logger.error(f"Serper API request failed with status: {resp.status}")
					return None
				return await resp.json()

	async def get_image(
			self,
			query: str,
			brand_model_id: Optional[int] = None,
			config_id: Optional[int] = None
	) -> Optional[ImageResponse]:
		if not self._api_key:
			return None

		if query in self._cache:
			return self._cache[query]

		db_cached = self._get_from_db_cache(brand_model_id, config_id, query)
		if db_cached:
			return db_cached

		try:
			data = await self._fetch_from_serper(query)
			if not data:
				self._cache[query] = None
				return None

			images = data.get("images") or data.get("items") or []
			if not images:
				logger.warning(f"Google Serper returned an empty image list for query '{query}'")
				self._cache[query] = None
				return None

			# Обрабатываем и кэшируем все 3 полученных изображения с приоритетами
			main_image_response = None
			save_images = os.getenv("SAVE_IMAGES", "0")

			for idx, img_data in enumerate(images[:3], start=1):
				image_url = img_data.get("imageUrl") or ""
				if not image_url:
					continue

				thumbnail_url = img_data.get("thumbnailUrl") or ""
				local_file_path = None
				if save_images == "1" and isinstance(thumbnail_url, str) and thumbnail_url:
					try:
						local_file_path = await self._save_thumbnail_url(
							query=f"{query}_p{idx}",
							image_url=image_url,
							thumbnail_url=thumbnail_url,
						)
					except Exception as e:
						logger.error(f"Failed to cache thumbnail locally for '{query}': {str(e)}")

				self._save_to_db_cache(brand_model_id, config_id, image_url, idx)

				if idx == 1:
					main_image_response = ImageResponse(
						title=img_data.get("title", ""),
						imageUrl=image_url,
						thumbnailUrl=thumbnail_url or None,
						imageWidth=img_data.get("imageWidth") or 0,
						imageHeight=img_data.get("imageHeight") or 0,
						source=img_data.get("source") or "",
						domain=img_data.get("domain") or "",
						link=img_data.get("link") or "",
						position=img_data.get("position") or 0,
					)

			if not main_image_response:
				self._cache[query] = None
				return None

			self._cache[query] = main_image_response
			return main_image_response

		except Exception as e:
			logger.error(f"Unexpected error in image retrieval process: {str(e)}", exc_info=True)
			self._cache[query] = None
			return None

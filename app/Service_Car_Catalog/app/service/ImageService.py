# app/service/ImageService.py
from __future__ import annotations

import base64
import hashlib
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

import aiohttp
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.schemas.image import ImageResponse


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
	"""Получение изображений через Serper API с поддержкой кэша БД и диска."""

	def __init__(self, *, api_key: Optional[str], db: Optional[Session] = None,
	             storage_dir: Optional[Path] = None) -> None:
		self._api_key = api_key
		self._db = db
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
			target_path.write_bytes(decoded)

		return str(target_path)

	async def _save_thumbnail_url(self, *, query: str, image_url: str, thumbnail_url: str) -> Optional[str]:
		if not thumbnail_url:
			return None

		if thumbnail_url.startswith("data:"):
			return self._save_embedded_image(query=query, image_url=image_url, thumbnail_data_url=thumbnail_url)

		file_key = f"{query}|{image_url}|{thumbnail_url}"
		file_name = hashlib.sha256(file_key.encode("utf-8")).hexdigest()[:24]

		try:
			timeout = aiohttp.ClientTimeout(total=7)
			async with aiohttp.ClientSession(timeout=timeout) as session:
				async with session.get(thumbnail_url) as resp:
					if resp.status < 200 or resp.status >= 300:
						return None
					content = await resp.read()
					content_type = resp.headers.get("Content-Type", "")
		except Exception:
			return None

		ext = "bin"
		if "image/" in content_type:
			ext = content_type.split("image/", 1)[1].split(";", 1)[0].strip() or "bin"
		elif "." in thumbnail_url.rsplit("/", 1)[-1]:
			ext = thumbnail_url.rsplit("/", 1)[-1].split(".", 1)[-1].split("?", 1)[0] or "bin"

		target_path = self._storage_dir / f"{file_name}.{ext}"
		if not target_path.exists():
			target_path.write_bytes(content)
		return str(target_path)

	def _get_from_db_cache(
			self,
			brand_model_id: Optional[int],
			config_id: Optional[int],
			query: str
	) -> Optional[ImageResponse]:
		if not self._db:
			return None

		cached_url = None
		source_label = ""

		# Чтение кэша карточек моделей
		if brand_model_id is not None:
			from app.models.BrandModelPhoto import BrandModelPhoto
			stmt = select(BrandModelPhoto.url).where(
				BrandModelPhoto.brand_model_id == brand_model_id
			).order_by(BrandModelPhoto.priority.asc())
			cached_url = self._db.execute(stmt).scalars().first()
			source_label = "DB_Brand_Cache"

		# Чтение кэша конфигураций
		elif config_id is not None:
			from app.models.CarConfigPhoto import CarConfigPhoto
			stmt = select(CarConfigPhoto.url).where(
				CarConfigPhoto.config_id == config_id
			).order_by(CarConfigPhoto.priority.asc())
			cached_url = self._db.execute(stmt).scalars().first()
			source_label = "DB_Config_Cache"

		if cached_url:
			img_resp = ImageResponse(
				title=query,
				imageUrl=cached_url,
				source=source_label
			)
			self._cache[query] = img_resp
			return img_resp

		return None

	def _save_to_db_cache(self, brand_model_id: Optional[int], config_id: Optional[int], url: str) -> None:
		if not self._db:
			return

		# Сохранение фото в кэш моделей
		if brand_model_id is not None:
			from app.models.BrandModelPhoto import BrandModelPhoto
			exists = self._db.query(BrandModelPhoto).filter_by(
				brand_model_id=brand_model_id,
				url=url
			).first()
			if not exists:
				p_exists = self._db.query(BrandModelPhoto).filter_by(
					brand_model_id=brand_model_id,
					priority=1
				).first()
				if not p_exists:
					photo = BrandModelPhoto(brand_model_id=brand_model_id, url=url, priority=1)
					self._db.add(photo)
					self._db.commit()

		# Сохранение фото в кэш конфигуратора
		elif config_id is not None:
			from app.models.CarConfigPhoto import CarConfigPhoto
			exists = self._db.query(CarConfigPhoto).filter_by(
				config_id=config_id,
				url=url
			).first()
			if not exists:
				p_exists = self._db.query(CarConfigPhoto).filter_by(
					config_id=config_id,
					priority=1
				).first()
				if not p_exists:
					photo = CarConfigPhoto(config_id=config_id, url=url, priority=1)
					self._db.add(photo)
					self._db.commit()

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
			async with session.post(url, json=payload, headers=headers) as resp:
				if resp.status < 200 or resp.status >= 300:
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
				self._cache[query] = None
				return None

			first = images[0]
			image_url = first.get("imageUrl") or ""
			if not image_url:
				self._cache[query] = None
				return None

			# Локальное сохранение файла
			thumbnail_url = first.get("thumbnailUrl") or ""
			local_file_path = None

			save_images = os.getenv("SAVE_IMAGES", "0")
			if save_images == "1" and isinstance(thumbnail_url, str) and thumbnail_url:
				local_file_path = await self._save_thumbnail_url(
					query=query,
					image_url=image_url,
					thumbnail_url=thumbnail_url,
				)

			image = ImageResponse(
				title=first.get("title", ""),
				imageUrl=image_url,
				thumbnailUrl=thumbnail_url or None,
				imageWidth=first.get("imageWidth") or 0,
				imageHeight=first.get("imageHeight") or 0,
				source=first.get("source") or "",
				domain=first.get("domain") or "",
				link=first.get("link") or "",
				position=first.get("position") or 0,
			)

			# 5. Сохраняем ссылку в базу данных для будущих запросов
			self._save_to_db_cache(brand_model_id, config_id, image_url)

			self._cache[query] = image
			return image

		except Exception:
			self._cache[query] = None
			return None

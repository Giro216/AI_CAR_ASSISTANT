from __future__ import annotations

import base64
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

import aiohttp

from app.schemas.image import ImageResponse


class ImageService(ABC):
    @abstractmethod
    async def get_image(self, query: str) -> Optional[ImageResponse]:
        """Вернуть объект изображения по поисковому запросу."""


class SerperImageService(ImageService):
    """Получение изображений через Serper API.

    Переменные окружения:
      - SERPER_API_KEY
    """

    def __init__(self, *, api_key: Optional[str], storage_dir: Optional[Path] = None) -> None:
        self._api_key = api_key
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

        # Стабильное имя файла, чтобы не плодить дубликаты.
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

    async def get_image(self, query: str) -> Optional[ImageResponse]:
        if not self._api_key:
            return None

        if query in self._cache:
            return self._cache[query]

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

        try:
            timeout = aiohttp.ClientTimeout(total=7)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status < 200 or resp.status >= 300:
                        self._cache[query] = None
                        return None
                    data = await resp.json()

            images = data.get("images") or data.get("items") or []
            if not images:
                self._cache[query] = None
                return None

            first = images[0]
            local_file_path = None
            thumbnail_url = first.get("thumbnailUrl") or ""
            if isinstance(thumbnail_url, str) and thumbnail_url:
                local_file_path = await self._save_thumbnail_url(
                    query=query,
                    image_url=first.get("imageUrl") or "",
                    thumbnail_url=thumbnail_url,
                )

            image = ImageResponse(
                title=first.get("title", ""),
                imageUrl=first.get("imageUrl") or "",
                thumbnailUrl=thumbnail_url or None,
                imageWidth=first.get("imageWidth") or 0,
                imageHeight=first.get("imageHeight") or 0,
                source=first.get("source") or "",
                domain=first.get("domain") or "",
                link=first.get("link") or "",
                position=first.get("position") or 0,
                # localFilePath=local_file_path,
            )

            # Если в ответе нет валидного url, считаем результат пустым.
            if not image.imageUrl:
                self._cache[query] = None
                return None

            self._cache[query] = image
            return image
        except Exception:
            self._cache[query] = None
            return None

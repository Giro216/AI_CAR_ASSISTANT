from __future__ import annotations

from abc import ABC, abstractmethod
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

    def __init__(self, *, api_key: Optional[str]) -> None:
        self._api_key = api_key
        self._cache: Dict[str, Optional[ImageResponse]] = {}

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
            image = ImageResponse(
                title=first.get("title", ""),
                imageUrl=first.get("imageUrl") or "",
                imageWidth=first.get("imageWidth") or 0,
                imageHeight=first.get("imageHeight") or 0,
                source=first.get("source") or "",
                domain=first.get("domain") or "",
                link=first.get("link") or "",
                position=first.get("position") or 0,
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

"""Mock/Stub реализация ImageService для тестирования.

Не делает реальные запросы к API, не расходует токены.
"""

from typing import Optional

from app.schemas.image import ImageResponse
from app.service.ImageService import ImageService


class MockImageService(ImageService):
	"""Mock сервис изображений - для тестирования без API запросов.

	Возвращает тестовые данные без обращения к реальному API.
	"""

	def __init__(self, *, fail_mode: bool = False):
		"""
		Args:
			fail_mode: Если True, всегда возвращает None (имитирует ошибку API)
		"""
		self._fail_mode = fail_mode
		self._call_count = 0

	async def get_image(self, query: str) -> Optional[ImageResponse]:
		"""Возвращает mock ответ без реального запроса к API."""
		self._call_count += 1

		if self._fail_mode:
			return None

		# Возвращаем консистентные тестовые данные
		return ImageResponse(
			title=f"Mock image for '{query}'",
			imageUrl=f"https://example.com/mock-image-{self._call_count}.jpg",
			thumbnailUrl=f"https://example.com/mock-thumbnail-{self._call_count}.jpg",
			imageWidth=800,
			imageHeight=600,
			source="mock-source",
			domain="example.com",
			link=f"https://example.com/link-{self._call_count}",
			position=1,
		)

	def get_call_count(self) -> int:
		"""Возвращает количество вызовов get_image."""
		return self._call_count

	def reset(self):
		"""Сброс счетчика для нового теста."""
		self._call_count = 0

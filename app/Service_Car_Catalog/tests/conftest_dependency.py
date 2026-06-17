"""Провайдеры зависимостей для тестирования.

Используются те же зависимости, но с переопределением на mock сервисы.
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.repository.CarsRepository import CarsRepository
from app.repository.InMemoryCarsRepository import InMemoryCarsRepository
from app.service.CarService import CarService
from app.service.ImageService import ImageService
from app.service.MockImageService import MockImageService


def get_db_test() -> Generator[Session, None, None]:
	"""Провайдер БД для тестов."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def get_image_service_test() -> ImageService:
	"""Провайдер mock сервиса изображений для тестов.

	Всегда возвращает mock - никогда не делает реальные запросы к API.
	"""
	return MockImageService()


def get_cars_repository_test() -> CarsRepository:
	"""Провайдер репозитория для тестов - всегда in-memory."""
	return InMemoryCarsRepository()


def get_car_service_test(
		repo: CarsRepository = None,
		image_service: ImageService = None,
) -> CarService:
	"""Провайдер CarService для тестов с mock зависимостями."""
	if repo is None:
		repo = get_cars_repository_test()
	if image_service is None:
		image_service = get_image_service_test()

	return CarService(repo=repo, image_service=image_service)

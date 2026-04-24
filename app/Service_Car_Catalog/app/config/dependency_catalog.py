"""Dependency Injection слой для каталога автомобилей.

Отдельным модулем, чтобы не мешать старым заготовкам в `dependency.py`.
"""

from __future__ import annotations

import os

from app.repository.cars_repository import CarsRepository, InMemoryCarsRepository
from app.service.carService import CarService
from app.service.imageService import SerperImageService, ImageService


def get_image_service() -> ImageService:
    """Провайдер сервиса изображений.

    Требует переменные окружения:
      - SERPER_API_KEY

    """

    api_key = os.getenv("SERPER_API_KEY")
    return SerperImageService(api_key=api_key)


def get_cars_repository() -> CarsRepository:
    # Заглушка на будущее: позже заменить на SQLAlchemyCarsRepository(...)
    return InMemoryCarsRepository()


def get_car_service() -> CarService:
    return CarService(repo=get_cars_repository(), image_service=get_image_service())

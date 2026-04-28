"""Dependency Injection слой для каталога автомобилей.

Отдельным модулем, чтобы не мешать старым заготовкам в `dependency.py`.
"""

from __future__ import annotations

import os
from pathlib import Path

from app.repository.cars_repository import CarsRepository, InMemoryCarsRepository
from app.service.carService import CarService
from app.service.imageService import SerperImageService, ImageService


def get_image_service() -> ImageService:
    """Провайдер сервиса изображений.

    Требует переменные окружения:
      - SERPER_API_KEY
      - IMAGE_STORAGE_DIR (optional)

    """

    api_key = os.getenv("SERPER_API_KEY")
    storage_dir = Path(os.getenv("IMAGE_STORAGE_DIR", "storage/images"))
    return SerperImageService(api_key=api_key, storage_dir=storage_dir)


def get_cars_repository() -> CarsRepository:
    # Заглушка на будущее: позже заменить на SQLAlchemyCarsRepository(...)
    return InMemoryCarsRepository()


def get_car_service() -> CarService:
    return CarService(repo=get_cars_repository(), image_service=get_image_service())

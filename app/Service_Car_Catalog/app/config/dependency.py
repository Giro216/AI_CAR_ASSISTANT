from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.repository.CarsRepository import CarsRepository
from app.repository.InMemoryCarsRepository import InMemoryCarsRepository
from app.repository.SQLAlchemyCarsRepository import SQLAlchemyCarsRepository
from app.service.carService import CarService
from app.service.imageService import SerperImageService, ImageService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_image_service() -> ImageService:
    """Провайдер сервиса изображений.

    Требует переменные окружения:
      - SERPER_API_KEY
      - IMAGE_STORAGE_DIR (optional)

    """

    api_key = os.getenv("SERPER_API_KEY")
    storage_dir = Path(os.getenv("IMAGE_STORAGE_DIR", "storage/images"))
    return SerperImageService(api_key=api_key, storage_dir=storage_dir)


def get_cars_repository(db: Session = Depends(get_db)) -> CarsRepository:
    if os.getenv("USE_IN_MEMORY") == "1":
        return InMemoryCarsRepository()
    return SQLAlchemyCarsRepository(db)


def get_car_service(
        repo: CarsRepository = Depends(get_cars_repository),
        image_service: ImageService = Depends(get_image_service),
) -> CarService:
    return CarService(repo=repo, image_service=image_service)

# app/config/dependency.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import redis
from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.config.redis import get_redis
from app.repository.CarsRepository import CarsRepository
from app.repository.SQLAlchemyCarsRepository import SQLAlchemyCarsRepository
from app.service.CarService import CarService
from app.service.ImageService import ImageService, SerperImageService


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
		db.commit()
	except Exception:
		db.rollback()
		raise
	finally:
		db.close()


def get_image_service(
		db: Session = Depends(get_db),
		redis_conn: redis.Redis = Depends(get_redis)
) -> ImageService:
	"""Провайдер сервиса изображений."""
	api_key = os.getenv("SERPER_API_KEY")
	storage_dir = Path(os.getenv("IMAGE_STORAGE_DIR", "storage/images"))

	return SerperImageService(api_key=api_key, storage_dir=storage_dir, db=db, redis_client=redis_conn)


def get_cars_repository(db: Session = Depends(get_db)) -> CarsRepository:
	return SQLAlchemyCarsRepository(db)


def get_car_service(
		repo: CarsRepository = Depends(get_cars_repository),
		image_service: ImageService = Depends(get_image_service),
		redis_conn: redis.Redis = Depends(get_redis)  # Внедряем Redis
) -> CarService:
	return CarService(repo=repo, image_service=image_service, redis_client=redis_conn)

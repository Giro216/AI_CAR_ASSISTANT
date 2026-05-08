"""API v1: каталог автомобилей.

Эндпоинты (пока без БД):
- GET /api/v1/cars
- GET /api/v1/cars/{car_id}
- GET /api/v1/cars/popular
- GET /api/v1/cars/search
- GET /api/v1/cars/filters/meta
- GET /api/v1/cars/{car_id}/similar
- GET /api/v1/cars/{car_id}/pricing
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.config.dependency import get_car_service
from app.schemas import CarDetailInfo, FiltersMeta, CarBasicInfo
from app.schemas.CarModelCard import CarModelCard
from app.service.carService import CarService

router = APIRouter()


@router.get("/", response_model=List[CarModelCard])
async def get_cars(
        # TODO добавить фильтры и сортировку
        service: CarService = Depends(get_car_service),
        brand_model_id: Optional[str] = Query(default=None),
        brand: Optional[str] = Query(default=None),
        model: Optional[str] = Query(default=None),
        sort: Optional[str] = Query(default=None, description="Пока заглушка"),
        limit: int = Query(default=10, ge=1, le=50),
        page: int = Query(default=1, ge=1),
):
    return await service.get_models(
        brand_model_id=brand_model_id,
        brand=brand,
        model=model,
        sort=sort,
        limit=limit,
        page=page,
    )


@router.get("/popular", response_model=List[CarModelCard])
async def get_popular_cars(
        service: CarService = Depends(get_car_service),
        limit: int = Query(default=3, ge=1, le=10),
):
    return await service.get_popular_cars(limit=limit)


@router.get("/search", response_model=List[CarModelCard])
async def search_cars(
        service: CarService = Depends(get_car_service),
        q: str = Query(..., min_length=1, max_length=200),
        limit: int = Query(default=20, ge=1, le=50),
):
    return await service.search(q=q, limit=limit)


@router.get("/filters/meta", response_model=FiltersMeta)
async def get_filters_meta(
        service: CarService = Depends(get_car_service)
):
    return await service.get_filters_meta()


@router.get("/{brand_model_id}/generations", response_model=List[CarBasicInfo])
async def get_generations(
        brand_model_id: str,
        service: CarService = Depends(get_car_service),
):
    return await service.get_models_generations(brand_model_id=brand_model_id)


@router.get("/{brand_model_id}/{body_type}/details", response_model=CarDetailInfo)
async def get_car_detail(
        brand_model_id: str,
        body_type: str,
        service: CarService = Depends(get_car_service),
):
    return await service.get_car_detail(brand_model_id=brand_model_id, body_type=body_type)

# @router.get("/{car_id}/pricing")
# async def get_car_pricing(
#         car_id: str,
#         service: CarService = Depends(get_car_service),
# ):
#     # Заглушка под будущее агрегирование pricing
#     return await service.get_car_pricing(car_id=car_id)

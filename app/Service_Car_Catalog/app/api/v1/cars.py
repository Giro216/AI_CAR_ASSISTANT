from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from app.config.auth import get_current_user_credentials, UserCredentials
from app.config.dependency import get_car_service
from app.schemas import FiltersMeta, CarBasicInfo, CarFullInfoConfig
from app.schemas.CarModelCard import CarModelCard
from app.schemas.CatalogData import CatalogData
from app.service.CarService import CarService

router = APIRouter()


@router.get("/", response_model=CatalogData)
async def get_cars(
		service: CarService = Depends(get_car_service),
		brand_model_id: Optional[str] = Query(default=None),
		brand: Optional[str] = Query(default=None),
		model: Optional[str] = Query(default=None),
		sort: Optional[str] = Query(default='popular'),
		limit: int = Query(default=12, ge=1, le=50),
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


@router.get("/search", response_model=CatalogData)
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


@router.get("/{brand_model_id}/{generation}/{body_type}/config", response_model=List[CarFullInfoConfig])
async def get_car_config(
		brand_model_id: str,
		generation: str,
		body_type: str,
		service: CarService = Depends(get_car_service),
):
	return await service.get_car_config(brand_model_id=brand_model_id, generation=generation, body_type=body_type)


@router.post("/favorites/{car_id}", status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
		car_id: str,
		current_user: UserCredentials = Depends(get_current_user_credentials),
		service: CarService = Depends(get_car_service),
):
	await service.add_to_favorites(user_id=current_user.id, car_id=car_id)
	return {"detail": "Автомобиль добавлен в избранное"}


@router.delete("/favorites/{car_id}", status_code=status.HTTP_200_OK)
async def remove_from_favorites(
		car_id: str,
		current_user: UserCredentials = Depends(get_current_user_credentials),
		service: CarService = Depends(get_car_service),
):
	await service.remove_from_favorites(user_id=current_user.id, car_id=car_id)
	return {"detail": "Автомобиль удален из избранного"}


@router.get("/favorites", response_model=List[CarModelCard])
async def get_my_favorites(
		current_user: UserCredentials = Depends(get_current_user_credentials),
		service: CarService = Depends(get_car_service),
):
	return await service.get_favorite_cars(user_id=current_user.id)

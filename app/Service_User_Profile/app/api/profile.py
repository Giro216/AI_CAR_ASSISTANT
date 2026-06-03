from fastapi import APIRouter, Depends, status
from app.dependencies.auth import get_profile_service, get_current_user_credentials, UserCredentials, \
	validate_internal_api_key
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter()

# 1. Внутренний эндпоинт для регистрации профиля (вызывается из Auth Service)
@router.post(
    "/",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_internal_api_key)]
)
async def create_profile(
    profile_data: ProfileCreate,
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.create_user_profile(profile_data)

# 2. Публичный эндпоинт получения своего профиля пользователем (через JWT)
@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: UserCredentials = Depends(get_current_user_credentials),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.get_user_profile(current_user.id)

# 3. Публичный эндпоинт изменения своего профиля (через JWT)
@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: UserCredentials = Depends(get_current_user_credentials),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.update_user_profile(current_user.id, profile_update)
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_profile_service, get_current_user_credentials, UserCredentials
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter()

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: UserCredentials = Depends(get_current_user_credentials),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.get_user_profile(current_user.id)

@router.put("/me", response_model=ProfileResponse)
async def update_or_create_my_profile(
    profile_update: ProfileUpdate,
    current_user: UserCredentials = Depends(get_current_user_credentials),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return await profile_service.upsert_user_profile(current_user.id, profile_update)
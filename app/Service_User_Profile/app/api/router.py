from fastapi import APIRouter
from app.api.profile import router as profile_router

api_router = APIRouter()
api_router.include_router(profile_router, prefix="/profiles", tags=["profiles"])
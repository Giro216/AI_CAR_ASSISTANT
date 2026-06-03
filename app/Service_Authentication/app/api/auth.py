from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_auth_service, get_current_user
from app.model.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.service.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.authenticate_user(credentials)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
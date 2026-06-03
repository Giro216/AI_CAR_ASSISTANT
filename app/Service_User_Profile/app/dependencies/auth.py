import uuid
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.repositories.profile_repository import ProfileRepository
from app.services.profile_service import ProfileService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/api/v1/auth/login")

class UserCredentials(BaseModel):
    id: uuid.UUID
    email: EmailStr

def get_profile_repository(db: AsyncSession = Depends(get_db)) -> ProfileRepository:
    return ProfileRepository(db)

def get_profile_service(profile_repo: ProfileRepository = Depends(get_profile_repository)) -> ProfileService:
    return ProfileService(profile_repo)

async def get_current_user_credentials(token: str = Depends(oauth2_scheme)) -> UserCredentials:
    """
    Математическая верификация токена на основе симметричного общего ключа SECRET_KEY.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный или просроченный токен авторизации",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None or email is None:
            raise credentials_exception
        return UserCredentials(id=uuid.UUID(user_id), email=email)
    except JWTError:
        raise credentials_exception


async def validate_internal_api_key(x_internal_key: str = Header(..., alias="X-Internal-Key")):
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен: неверный или отсутствующий токен авторизации микросервиса."
        )
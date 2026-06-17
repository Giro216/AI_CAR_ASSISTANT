import os
import uuid
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr

# Кастомный класс для мягкой проверки токена
class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str | None:
        try:
            return await super().__call__(request)
        except HTTPException as e:
            if e.status_code == status.HTTP_401_UNAUTHORIZED:
                return None
            raise e


optional_oauth2_scheme = OptionalOAuth2PasswordBearer(tokenUrl="http://localhost:8003/api/v1/auth/login", auto_error=False)


class UserCredentials(BaseModel):
    id: uuid.UUID
    email: EmailStr

async def get_optional_user_credentials(token: str | None = Depends(optional_oauth2_scheme)) -> UserCredentials | None:
    """
    Опциональная верификация токена. Если токен есть - валидирует его.
    Если токена нет - возвращает None (для гостевого режима).
    """
    if not token:
        return None
        
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM", "HS256")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None or email is None:
            return None
        return UserCredentials(id=uuid.UUID(user_id), email=email)
    except JWTError:
        # Если токен был передан, но он сломан/истек - возвращаем ошибку 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )
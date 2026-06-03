import logging
import httpx
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import get_password_hash
from app.model.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegisterInput, UserLogin, Token

logger = logging.getLogger("auth_service")


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_in: UserRegisterInput) -> User:
        # Проверяем уникальность email в Auth DB
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует."
            )

        # Создаем пользователя во внутренней базе Auth DB
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            password_hash=hashed_password,
            is_active=True
        )
        created_user = await self.user_repo.create(db_user)

        # Формируем динамический конверт для User Service
        user_service_payload = {
            "user_id": str(created_user.id),
            **user_in.profile  # Распаковка всех переданных полей
        }

        logger.info(f"User service payload: {user_service_payload}")

        # Отправляем запрос в User Service
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "X-Internal-Key": settings.INTERNAL_API_KEY
                }

                logger.info(f"Sending request to User Service at {settings.USER_SERVICE_PROFILE_URL} with headers {headers} and payload {user_service_payload}")
                response = await client.post(
                    settings.USER_SERVICE_PROFILE_URL,
                    json=user_service_payload,
                    headers=headers,
                    timeout=5.0
                )
                
                if response.status_code not in (200, 201):
                    logger.error(
                        f"User Service returned error {response.status_code}: {response.text}. "
                        f"Initiating rollback for user {created_user.id}."
                    )
                    await self._rollback_registration(created_user.id)
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Ошибка создания профиля пользователя на внешнем сервисе. Регистрация отменена."
                    )

            except (httpx.RequestError, httpx.TimeoutException) as exc:
                logger.error(
                    f"Connection to User Service failed: {str(exc)}. "
                    f"Initiating rollback for user {created_user.id}."
                )
                await self._rollback_registration(created_user.id)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Сервис создания профилей временно недоступен. Регистрация отменена."
                )

            return created_user

    async def _rollback_registration(self, user_id) -> None:
        try:
            await self.user_repo.delete(user_id)
        except Exception as e:
            logger.critical(
                f"CRITICAL: Rollback failed for user_id {user_id}. "
                f"Database integrity may be compromised. Error: {str(e)}"
            )

    async def authenticate_user(self, credentials: UserLogin) -> Token:
        from app.core.security import verify_password, create_access_token

        user = await self.user_repo.get_by_email(credentials.email)
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Учетная запись пользователя деактивирована"
            )

        access_token = create_access_token(subject=user.id, email=user.email)
        return Token(access_token=access_token, token_type="bearer")
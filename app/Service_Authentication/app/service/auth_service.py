from fastapi import HTTPException, status
from app.core.security import get_password_hash
from app.model.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegisterInput, UserLogin, Token


class AuthService:
	def __init__(self, user_repo: UserRepository):
		self.user_repo = user_repo

	async def register_user(self, user_in: UserRegisterInput) -> User:
		existing_user = await self.user_repo.get_by_email(user_in.email)
		if existing_user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Пользователь с таким email уже существует."
			)

		db_user = User(
			email=user_in.email,
			password_hash=get_password_hash(user_in.password),
			is_active=True
		)
		return await self.user_repo.create(db_user)

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
				detail="Учетная запись деактивирована."
			)

		access_token = create_access_token(subject=user.id, email=user.email)
		return Token(access_token=access_token, token_type="bearer")
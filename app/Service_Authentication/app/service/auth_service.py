from fastapi import HTTPException, status

from app.core.security import get_password_hash, verify_password, create_access_token
from app.model.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, Token


class AuthService:
	def __init__(self, user_repo: UserRepository):
		self.user_repo = user_repo

	async def register_user(self, user_in: UserCreate) -> User:
		existing_user = await self.user_repo.get_by_email(user_in.email)
		if existing_user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="A user with this email address already exists."
			)

		hashed_password = get_password_hash(user_in.password)
		db_user = User(
			email=user_in.email,
			password_hash=hashed_password,
			is_active=True
		)
		return await self.user_repo.create(db_user)

	async def authenticate_user(self, credentials: UserLogin) -> Token:
		user = await self.user_repo.get_by_email(credentials.email)
		if not user or not verify_password(credentials.password, user.password_hash):
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect email or password",
				headers={"WWW-Authenticate": "Bearer"},
			)

		if not user.is_active:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Inactive user account"
			)

		access_token = create_access_token(subject=user.id, email=user.email)
		return Token(access_token=access_token, token_type="bearer")
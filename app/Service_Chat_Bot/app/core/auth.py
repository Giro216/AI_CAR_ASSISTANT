import os
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserCredentials(BaseModel):
	id: uuid.UUID
	email: EmailStr


async def get_current_user_credentials(token: str = Depends(oauth2_scheme)) -> UserCredentials:
	secret_key = os.getenv("SECRET_KEY")
	algorithm = os.getenv("ALGORITHM", "HS256")

	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Недействительный или просроченный токен авторизации",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, secret_key, algorithms=[algorithm])
		user_id: str = payload.get("sub")
		email: str = payload.get("email")
		if user_id is None or email is None:
			raise credentials_exception
		return UserCredentials(id=uuid.UUID(user_id), email=email)
	except JWTError:
		raise credentials_exception
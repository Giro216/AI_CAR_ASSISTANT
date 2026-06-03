import uuid
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserBase(BaseModel):
	email: EmailStr


class UserRegisterInput(UserBase):
	password: str = Field(..., min_length=8, description="Пароль должен быть не менее 8 символов")

	profile: Dict[str, Any] = Field(
		default_factory=dict,
		description="Динамический пакет данных профиля для User Service"
	)


class UserLogin(UserBase):
	password: str


class UserResponse(UserBase):
	id: uuid.UUID
	is_active: bool
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"


class TokenData(BaseModel):
	user_id: uuid.UUID | None = None
	email: EmailStr | None = None

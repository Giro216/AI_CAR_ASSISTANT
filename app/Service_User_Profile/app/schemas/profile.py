import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
	first_name: Optional[str] = Field(None, max_length=100, description="Имя пользователя")
	last_name: Optional[str] = Field(None, max_length=100, description="Фамилия пользователя")
	city: Optional[str] = Field(None, max_length=100, description="Город проживания")

	age: Optional[int] = Field(None, ge=0, le=120, description="Возраст пользователя")
	children_count: Optional[int] = Field(None, ge=0, le=50, description="Количество детей")


class ProfileUpdate(ProfileBase):
	# Любые поля при обновлении опциональны
	pass


class ProfileResponse(ProfileBase):
	user_id: uuid.UUID
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
	first_name: Optional[str] = None
	last_name: Optional[str] = None
	phone: Optional[str] = None
	city: Optional[str] = None
	preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProfileCreate(ProfileBase):
	user_id: uuid.UUID

	# Разрешаем передачу любых дополнительных полей при регистрации
	model_config = ConfigDict(extra="allow")


class ProfileUpdate(ProfileBase):
	# Разрешаем передачу любых полей при редактировании
	model_config = ConfigDict(extra="allow")


class ProfileResponse(ProfileBase):
	user_id: uuid.UUID
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)
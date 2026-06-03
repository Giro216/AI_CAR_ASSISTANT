from typing import Any, Dict
from fastapi import HTTPException, status
from app.models.profile import Profile
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
	def __init__(self, profile_repo: ProfileRepository):
		self.profile_repo = profile_repo

	async def create_user_profile(self, profile_in: ProfileCreate) -> Profile:
		existing_profile = await self.profile_repo.get(profile_in.user_id)
		if existing_profile:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Профиль для данного пользователя уже существует."
			)

		# Разделяем фиксированные поля и кастомные
		input_data = profile_in.model_dump()
		base_fields = {"user_id", "first_name", "last_name", "phone", "city"}

		# Собираем все дополнительные поля в словарь preferences
		extra_preferences = {k: v for k, v in input_data.items() if k not in base_fields and k != "preferences"}
		merged_preferences = {**(profile_in.preferences or {}), **extra_preferences}

		db_profile = Profile(
			user_id=profile_in.user_id,
			first_name=profile_in.first_name,
			last_name=profile_in.last_name,
			phone=profile_in.phone,
			city=profile_in.city,
			preferences=merged_preferences
		)
		return await self.profile_repo.create(db_profile)

	async def get_user_profile(self, user_id: Any) -> Profile:
		profile = await self.profile_repo.get(user_id)
		if not profile:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Профиль пользователя не найден."
			)
		return profile

	async def update_user_profile(self, user_id: Any, profile_update: ProfileUpdate) -> Profile:
		profile = await self.get_user_profile(user_id)

		update_data = profile_update.model_dump(exclude_unset=True)
		base_fields = {"first_name", "last_name", "phone", "city"}

		# Обновляем фиксированные поля
		for field in base_fields:
			if field in update_data:
				setattr(profile, field, update_data[field])

		# Обновляем динамические preferences
		extra_updates = {k: v for k, v in update_data.items() if k not in base_fields and k != "preferences"}
		nested_preferences_update = update_data.get("preferences", {})

		if profile.preferences is None:
			profile.preferences = {}

		profile.preferences = {
			**profile.preferences,
			**nested_preferences_update,
			**extra_updates
		}

		await self.profile_repo.db_session.flush()
		return profile
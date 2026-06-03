from typing import Any
from fastapi import HTTPException, status
from app.models.profile import Profile
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileUpdate


class ProfileService:
	def __init__(self, profile_repo: ProfileRepository):
		self.profile_repo = profile_repo

	async def get_user_profile(self, user_id: Any) -> Profile:
		profile = await self.profile_repo.get(user_id)
		if not profile:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Профиль пользователя еще не создан. Пожалуйста, заполните личную информацию."
			)
		return profile

	async def upsert_user_profile(self, user_id: Any, profile_update: ProfileUpdate) -> Profile:
		profile = await self.profile_repo.get(user_id)
		update_data = profile_update.model_dump(exclude_unset=True)

		allowed_fields = {"first_name", "last_name", "city", "age", "children_count"}

		if not profile:
			# Создаем новый профиль со строгим списком полей
			profile = Profile(
				user_id=user_id,
				first_name=update_data.get("first_name"),
				last_name=update_data.get("last_name"),
				city=update_data.get("city"),
				age=update_data.get("age"),
				children_count=update_data.get("children_count")
			)
			return await self.profile_repo.create(profile)

		# Если профиль существует, обновляем только пришедшие валидные поля
		for field in allowed_fields:
			if field in update_data:
				setattr(profile, field, update_data[field])

		await self.profile_repo.db_session.flush()
		return profile
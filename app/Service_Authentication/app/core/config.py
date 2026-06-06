# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	PROJECT_NAME: str = "Car AI Assistant Auth Service"
	API_V1_STR: str = "/api/v1"
	SECRET_KEY: str
	INTERNAL_API_KEY: str
	ALGORITHM: str = "HS256"
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

	DATABASE_URL: str

	USER_SERVICE_PROFILE_URL: str

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore"
	)


settings = Settings()
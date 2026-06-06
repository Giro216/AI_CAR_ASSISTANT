from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	PROJECT_NAME: str = "Car AI Assistant User Profile Service"
	API_V1_STR: str = "/api/v1"
	SECRET_KEY: str
	INTERNAL_API_KEY: str
	ALGORITHM: str = "HS256"

	DATABASE_URL: str

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore"
	)


settings = Settings()
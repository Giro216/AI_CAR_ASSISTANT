import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
	BASE_URL: str = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
	DATABASE_URL: str | None = os.getenv("DATABASE_URL")
	MODEL_NAME: str = os.getenv("AI_MODEL", "z-ai/glm-4.5-air")
	MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1200"))
	SUMMARY_MAX_TOKENS: int = int(os.getenv("SUMMARY_MAX_TOKENS", "400"))
	TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))

	class Config:
		env_file = ".env"


settings = Settings()

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
	BASE_URL: str = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
	DATABASE_URL: str | None = os.getenv("DATABASE_URL")
	MODEL_NAME: str = os.getenv("AI_MODEL", "z-ai/glm-4.5-air")
	MAX_AUTH_USER_RESPONSE_TOKENS: int = int(os.getenv("MAX_AUTH_USER_RESPONSE_TOKENS", "1200"))
	MAX_AUTH_USER_MESSAGES: int = int(os.getenv("MAX_AUTH_USER_MESSAGES", "40"))
	MAX_GUEST_RESPONSE_TOKENS: int = int(os.getenv("MAX_GUEST_RESPONSE_TOKENS", "500"))
	MAX_GUEST_MESSAGES: int = int(os.getenv("MAX_GUEST_MESSAGES", "16"))
	SUMMARY_MAX_TOKENS: int = int(os.getenv("SUMMARY_MAX_TOKENS", "500"))
	TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
	MAX_AGENT_STEPS: int = int(os.getenv("MAX_AGENT_STEPS", "12"))

	USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL")
	CATALOG_SERVICE_URL: str = os.getenv("CATALOG_SERVICE_URL")

	SERPER_API_KEY: str = os.getenv("SERPER_API_KEY")

	class Config:
		env_file = ".env"


settings = Settings()

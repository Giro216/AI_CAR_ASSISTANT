from openai import OpenAI

from app.core.config import settings

client = OpenAI(
	base_url=settings.BASE_URL,
	api_key=settings.OPENROUTER_API_KEY,
)

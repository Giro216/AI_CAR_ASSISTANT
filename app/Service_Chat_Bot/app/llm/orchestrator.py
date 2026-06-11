import json
import os
from typing import List, Optional
import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.core.promts import GUARD_PROMPT, SYSTEM_PROMPT
from app.llm.tools import AI_TOOLS

logger = get_logger(__name__)


class LLMOrchestrator:
	def __init__(self) -> None:
		self.client = AsyncOpenAI(api_key=settings.OPENROUTER_API_KEY, base_url=settings.BASE_URL)
		self.model_name = settings.MODEL_NAME

		# Внутренние URL-адреса микросервисов в Docker-сети с гарантированными косыми чертами
		self.user_service_url = settings.USER_SERVICE_URL.rstrip("/") + "/me"
		self.catalog_service_url = settings.CATALOG_SERVICE_URL.rstrip("/")

	def _compact_messages(self, messages: list[dict], limit: int = 200) -> list[dict]:
		compact: list[dict] = []
		for item in messages:
			if not isinstance(item, dict):
				role = getattr(item, "role", "assistant")
				content = getattr(item, "content", "") or ""
			else:
				role = item.get("role")
				content = item.get("content", "") or ""

			content_str = str(content) + "\n"
			compact.append({"role": role, "content": content_str})
		return compact

	def _log_request(self, model: str, messages: list[dict], max_tokens: int) -> None:
		logger.info(
			"LLM outbound request | model=%s | max_tokens=%s | messages=%s",
			model,
			max_tokens,
			self._compact_messages(messages),
		)

	def _log_response(self, content: str) -> None:
		logger.info("LLM response | content=%s", (content[:400] + "...") if len(content) > 400 else content)

	async def _call_get_user_profile(self, token: Optional[str]) -> str:
		if not token:
			logger.info("Tool 'get_user_profile' triggered, but user is anonymous (guest).")
			return "Пользователь не авторизован (гость). Личная информация о профиле недоступна."

		async with httpx.AsyncClient(follow_redirects=True) as client:
			try:
				headers = {"Authorization": f"Bearer {token}"}
				response = await client.get(self.user_service_url, headers=headers, timeout=5.0)
				if response.status_code == 200:
					logger.info("Successfully fetched user profile via Tool Calling.")
					return response.text
				return f"Не удалось получить профиль. Статус ответа: {response.status_code}"
			except Exception as e:
				logger.error(f"Error in 'get_user_profile' tool: {str(e)}")
				return "Ошибка подключения к сервису профилей пользователей."

	async def _call_search_cars_catalog(self, brand: Optional[str], model: Optional[str]) -> str:
		logger.info(
			f"Tool 'search_cars_catalog' triggered. Brand: {brand}, Model: {model}. Fetching from car-catalog...")

		async with httpx.AsyncClient(follow_redirects=True) as client:
			try:
				params = {}
				if brand:
					params["brand"] = brand
				if model:
					params["model"] = model

				response = await client.get(self.catalog_service_url, params=params, timeout=5.0)
				if response.status_code == 200:
					logger.info("Successfully searched cars catalog via Tool Calling.")
					return response.text
				return f"Не удалось выполнить поиск в каталоге. Статус ответа: {response.status_code}"
			except Exception as e:
				logger.error(f"Error in 'search_cars_catalog' tool: {str(e)}")
				return "Ошибка подключения к сервису каталога автомобилей."

	async def _call_web_search(self, query: str) -> str:
		if not settings.SERPER_API_KEY:
			logger.warning("Serper API Key is missing in .env. Web search tool is offline.")
			return "Поисковая система временно недоступна."

		logger.info(f"Tool 'web_search' triggered. Query: '{query}'")
		url = "https://google.serper.dev/search"
		payload = {"q": query, "gl": "ru", "hl": "ru"}
		headers = {
			"X-API-KEY": settings.SERPER_API_KEY,
			"Content-Type": "application/json"
		}

		async with httpx.AsyncClient(follow_redirects=True) as client:
			try:
				response = await client.post(url, json=payload, headers=headers, timeout=6.0)
				if response.status_code == 200:
					data = response.json()
					organic_results = data.get("organic", [])

					formatted_results = []
					for item in organic_results[:3]:
						formatted_results.append(
							f"Заголовок: {item.get('title')}\n"
							f"Текст: {item.get('snippet')}\n"
							f"Ссылка: {item.get('link')}\n"
						)
					return "\n".join(formatted_results) or "Ничего не найдено в интернете по вашему запросу."

				return f"Ошибка поисковой системы. Статус ответа: {response.status_code}"
			except Exception as e:
				logger.error(f"Error in 'web_search' tool: {str(e)}")
				return "Ошибка подключения к внешней поисковой системе."

	async def generate_reply(self, messages: list[dict], max_tokens: int = 1000, token: Optional[str] = None) -> str:
		request_messages = [{"role": "system", "content": SYSTEM_PROMPT + GUARD_PROMPT}] + messages

		try:
			local_messages = [dict(msg) for msg in request_messages]

			step_count = 0
			max_steps = 10

			while step_count < max_steps:
				step_count += 1
				self._log_request(self.model_name, local_messages, max_tokens)

				response = await self.client.chat.completions.create(
					model=self.model_name,
					messages=local_messages,
					max_tokens=max_tokens,
					tools=AI_TOOLS,
					tool_choice="auto"
				)

				response_message = response.choices[0].message
				tool_calls = response_message.tool_calls

				# Если модель запрашивает один или несколько инструментов на данном шаге
				if tool_calls:
					logger.info(f"GLM model requested {len(tool_calls)} tool calls (Step {step_count}/5).")
					local_messages.append(response_message)

					for tool_call in tool_calls:
						function_name = tool_call.function.name
						function_args = json.loads(tool_call.function.arguments)

						tool_result = ""

						if function_name == "get_user_profile":
							tool_result = await self._call_get_user_profile(token)

						elif function_name == "search_cars_catalog":
							brand = function_args.get("brand")
							model = function_args.get("model")
							tool_result = await self._call_search_cars_catalog(brand, model)

						elif function_name == "web_search":
							query = function_args.get("query")
							tool_result = await self._call_web_search(query)

						else:
							tool_result = f"Ошибка: неизвестная функция {function_name}"

						local_messages.append({
							"tool_call_id": tool_call.id,
							"role": "tool",
							"name": function_name,
							"content": tool_result,
						})
						logger.info(f"Tool {function_name} executed and returned data to LLM.")
					continue

				reply_content = response_message.content or ""
				self._log_response(reply_content)
				return reply_content

			logger.warning("Agent loop reached maximum step limit. Preventing further generation.")
			return "Извините, обработка вашего запроса заняла слишком много шагов. Сформулируйте ваш вопрос точнее."

		except Exception as e:
			logger.error(f"Error in LLMOrchestrator generation: {str(e)}", exc_info=True)
			return "Извините, произошла техническая ошибка при обработке вашего запроса."
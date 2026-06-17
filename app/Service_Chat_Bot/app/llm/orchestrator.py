# app/llm/orchestrator.py в Service_Chat_Bot
import asyncio
import json
import os
from typing import List, Optional
import httpx
from anyio import to_thread
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.llm.tools import AI_TOOLS
from app.core.promts import GUARD_PROMPT, SYSTEM_PROMPT, GUEST_QUOTA_CLOSING, SUMMARY_PROMPT

logger = get_logger(__name__)


class LLMOrchestrator:
	def __init__(self) -> None:
		self.client = AsyncOpenAI(api_key=settings.OPENROUTER_API_KEY, base_url=settings.BASE_URL)
		self.model_name = settings.MODEL_NAME
		self.max_steps = settings.MAX_AGENT_STEPS

		# Внутренние URL-адреса микросервисов в Docker-сети с гарантированными косыми чертами
		self.user_service_url = settings.USER_SERVICE_URL.rstrip("/") + "/me"
		self.catalog_service_url = settings.CATALOG_SERVICE_URL.rstrip("/")

	# Summarizes a batch using the previous summary as context.
	async def summarize_messages(self, previous_summary: str, batch: list[dict]) -> str:
		batch_lines = [f"{item['role']}: {item['content']}" for item in batch]
		payload = "\n".join(batch_lines)
		content = f"Previous summary:\n{previous_summary}\n\nNew messages:\n{payload}"
		self._log_request(settings.MODEL_NAME, [
			{"role": "system", "content": SUMMARY_PROMPT},
			{"role": "user", "content": content},
		], settings.SUMMARY_MAX_TOKENS)

		response = await to_thread.run_sync(
			lambda: self.client.chat.completions.create(
				model=settings.MODEL_NAME,
				messages=[
					{"role": "system", "content": SUMMARY_PROMPT},
					{"role": "user", "content": content},
				],
				max_tokens=settings.SUMMARY_MAX_TOKENS,
				temperature=0.2,
			)
		)

		choices = getattr(response, "choices", None) or []
		if not choices or not getattr(choices[0], "message", None):
			return previous_summary

		summary = choices[0].message.content or previous_summary
		self._log_response(summary)
		return summary

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
		logger.info(f"--- OUTBOUND LLM REQUEST ({model}) [max_tokens: {max_tokens}] ---")
		for msg in messages[-3:]:
			if not isinstance(msg, dict):
				role = getattr(msg, "role", "assistant")
				content = getattr(msg, "content", "") or ""
			else:
				role = msg.get("role")
				content = msg.get("content", "") or ""

			content_preview = str(content).replace('\n', ' ').strip()
			if len(content_preview) > 120:
				content_preview = content_preview[:120] + "..."
			logger.info(f"  [{role.upper()}]: {content_preview}")
		logger.info("------------------------------------------------------------------")

	def _log_response(self, content: str) -> None:
		content_preview = str(content).replace('\n', ' ').strip()
		if len(content_preview) > 120:
			content_preview = content_preview[:120] + "..."
		logger.info(f"--- INBOUND LLM RESPONSE: {content_preview}")

	async def _fetch_user_profile_data(self, token: Optional[str]) -> str:
		if not token:
			return "Пользователь не авторизован (гость). Личная информация отсутствует."

		async with httpx.AsyncClient(follow_redirects=True) as client:
			try:
				headers = {"Authorization": f"Bearer {token}"}
				response = await client.get(self.user_service_url, headers=headers, timeout=3.0)
				if response.status_code == 200:
					return response.text
				return "Профиль пуст."
			except Exception as e:
				logger.error(f"Error fetching proactive profile: {str(e)}")
				return "Профиль временно недоступен."

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

				response = await client.get(self.catalog_service_url, params=params, timeout=10.0)
				if response.status_code == 200:
					logger.info("Successfully searched cars catalog via Tool Calling.")

					try:
						data = response.json()
						if "founded_cars" in data:
							minimal_cars = []
							for car in data["founded_cars"]:
								minimal_cars.append({
									"brand_model_id": str(car.get("brand_model_id")),
									"brand": car.get("brand"),
									"model": car.get("model"),
									"start_year": car.get("start_year"),
									"end_year": car.get("end_year")
								})
							compact_data = {
								"cars_count": data.get("cars_count", 0),
								"founded_cars": minimal_cars
							}
							return json.dumps(compact_data, ensure_ascii=False)
					except Exception:
						pass
					return response.text
				return f"Не найдено. Статус: {response.status_code}"
			except Exception as e:
				logger.error(f"Error in catalog search: {str(e)}")
				return "Сервис каталога недоступен."

	async def _call_validate_cars_in_catalog(self, cars: list[dict]) -> str:
		logger.info(f"Tool 'validate_cars_in_catalog' triggered for {len(cars)} cars. Running parallel checks...")
		if not cars:
			return "Список для проверки пуст."

		tasks = []
		for car in cars:
			brand = car.get("brand")
			model = car.get("model")
			tasks.append(self._call_search_cars_catalog(brand, model))

		results = await asyncio.gather(*tasks)

		aggregated_report = []
		for car, res in zip(cars, results):
			aggregated_report.append(
				f"Запрос проверки: {car.get('brand')} {car.get('model')}\n"
				f"Результат в БД: {res}\n"
				f"-------------------"
			)
		return "\n".join(aggregated_report)

	async def _call_single_web_search(self, query: str) -> str:
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
					for item in organic_results[:2]:
						formatted_results.append(
							f"Заголовок: {item.get('title')}\n"
							f"Текст: {item.get('snippet')}\n"
						)
					return "\n".join(formatted_results) or "Ничего не найдено."

				return f"Ошибка поиска. Статус: {response.status_code}"
			except Exception as e:
				logger.error(f"Error in single web search: {str(e)}")
				return "Ошибка подключения к поиску."

	async def _call_batch_web_search(self, queries: list[dict]) -> str:
		logger.info(f"Tool 'batch_web_search' triggered for {len(queries)} queries. Running parallel searches...")
		if not queries:
			return "Список поисковых запросов пуст."

		tasks = []
		for q_item in queries:
			query_str = q_item.get("query")
			tasks.append(self._call_single_web_search(query_str))

		results = await asyncio.gather(*tasks)

		aggregated_report = []
		for q_item, res in zip(queries, results):
			aggregated_report.append(
				f"Автомобиль: {q_item.get('car_name')}\n"
				f"Результаты поиска в интернете:\n{res}\n"
				f"=================================="
			)
		return "\n".join(aggregated_report)

	async def generate_reply(
			self,
			messages: list[dict],
			max_tokens: int = 1000,
			token: Optional[str] = None,
			is_guest: bool = True,
			current_message_count: int = 0,
			max_messages: int = 12
	) -> str:
		try:
			is_new_chat = len(messages) <= 1

			profile_context = ""
			if is_new_chat and token:
				logger.info("New chat session detected. Proactively fetching user profile from user-service...")
				profile_data = await self._fetch_user_profile_data(token)
				profile_context = f"Данные профиля собеседника: {profile_data}\n\n"

			quota_directive = await self.QuotaDirectiveMsg(current_message_count, is_guest, max_messages)

			# Формируем объединенный системный промпт
			combined_system_content = (
				f"{profile_context}\n\n"
				f"{quota_directive}\n\n"
				f"{GUARD_PROMPT}\n\n"
				f"{SYSTEM_PROMPT}"
			)

			local_messages = [dict(msg) for msg in messages]

			system_index = -1
			for idx, msg in enumerate(local_messages):
				if msg.get("role") == "system":
					system_index = idx
					break

			if system_index != -1:
				local_messages[system_index]["content"] = combined_system_content
			else:
				local_messages.insert(0, {"role": "system", "content": combined_system_content})

			step_count = 0
			max_steps = self.max_steps

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

				if tool_calls:
					logger.info(f"GLM model requested {len(tool_calls)} tool calls (Step {step_count}/{max_steps}).")
					local_messages.append(response_message)

					for tool_call in tool_calls:
						function_name = tool_call.function.name
						function_args = json.loads(tool_call.function.arguments)

						tool_result = ""

						# Роутинг пакетных инструментов
						if function_name == "validate_cars_in_catalog":
							cars_list = function_args.get("cars", [])
							tool_result = await self._call_validate_cars_in_catalog(cars_list)

						elif function_name == "batch_web_search":
							queries_list = function_args.get("queries", [])
							tool_result = await self._call_batch_web_search(queries_list)

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

	async def QuotaDirectiveMsg(self, current_message_count: int, is_guest: bool, max_messages: int) -> str:
		remaining_messages = max(0, max_messages - current_message_count)
		remaining_assistant_turns = remaining_messages // 2

		quota_directive = ""
		if is_guest:
			quota_directive = (
				f"ТАРИФНЫЙ ПЛАН: ГОСТЬ. Всего лимит диалога: {max_messages} сообщений. "
				f"Сейчас идет {current_message_count + 1}-е сообщение из {max_messages}.\n"
			)
			# Если осталось 2 или меньше ответа ИИ до жесткой блокировки
			if remaining_assistant_turns <= 2:
				quota_directive += GUEST_QUOTA_CLOSING
		else:
			quota_directive = (
				f"ТАРИФНЫЙ ПЛАН: АВТОРИЗОВАННЫЙ. Шаг диалога {current_message_count + 1} из {max_messages}.\n"
			)
			if remaining_assistant_turns <= 5:
				quota_directive += (
					f"ВНИМАНИЕ: Подходит к концу лимит диалога ({max_messages} сообщений). "
					"Пожалуйста, закругляйся, подводи итоги и выдавай финальные рекомендации."
				)
		return quota_directive

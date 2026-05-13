from anyio import to_thread

from app.core.promts import SYSTEM_PROMPT, SUMMARY_PROMPT
from app.core.config import settings
from app.core.logger import get_logger
from app.llm.client import client

logger = get_logger(__name__)


class ChatOrchestrator:
	# Truncates message content for safe logging.
	def _compact_messages(self, messages: list[dict], limit: int = 200) -> list[dict]:
		compact: list[dict] = []
		for item in messages:
			content = item.get("content", "")
			# if len(content) > limit:
			# 	content = content[:limit] + "..."
			compact.append({"role": item.get("role"), "content": content})
		return compact

	# Logs outbound LLM request parameters.
	def _log_request(self, model: str, messages: list[dict], max_tokens: int) -> None:
		logger.info(
			"LLM request | model=%s | max_tokens=%s | messages=%s",
			model,
			max_tokens,
			self._compact_messages(messages),
		)

	# Logs the LLM response content.
	def _log_response(self, content: str) -> None:
		logger.info("LLM response | content=%s", content)

	async def generate_reply(self, messages: list[dict]) -> str:
		request_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
		self._log_request(settings.MODEL_NAME, request_messages, settings.MAX_TOKENS)

		response = await to_thread.run_sync(
			lambda: client.chat.completions.create(
				model=settings.MODEL_NAME,
				messages=request_messages,
				max_tokens=settings.MAX_TOKENS,
				temperature=settings.TEMPERATURE,
			)
		)

		choices = getattr(response, "choices", None) or []
		if not choices or not getattr(choices[0], "message", None):
			return ""

		reply = choices[0].message.content or ""
		self._log_response(reply)
		return reply

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
			lambda: client.chat.completions.create(
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

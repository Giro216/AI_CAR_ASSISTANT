import uuid
from typing import List, Optional
from fastapi import HTTPException, status

from app.core.config import settings
from app.llm.orchestrator import LLMOrchestrator
from app.repositoriy.conversation_repository_protocol import ConversationRepository
from app.service.summaryService import SummaryService


class ChatService:
	def __init__(
			self,
			repository: ConversationRepository,
			orchestrator: LLMOrchestrator | None = None,
			summary_service: SummaryService | None = None,
	) -> None:
		self._repository = repository
		self._orchestrator = orchestrator or LLMOrchestrator()
		self._summary_service = summary_service or SummaryService(self._repository, self._orchestrator)

	async def handle_message(
		self, 
		user_id: str, 
		message: str, 
		conversation_id: str, 
		is_guest: bool = True,
		token: Optional[str] = None
	) -> tuple[str, str]:
		try:
			conversation_id = self._repository.get_or_create_conversation_id(user_id, conversation_id)
		except ValueError as e:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail=str(e)
			)

		max_messages = settings.MAX_GUEST_MESSAGES if is_guest else settings.MAX_AUTH_USER_MESSAGES
		max_response_tokens = settings.MAX_GUEST_RESPONSE_TOKENS if is_guest else settings.MAX_AUTH_USER_RESPONSE_TOKENS

		current_message_count = self._repository.count_messages(conversation_id)
		if current_message_count >= max_messages:
			error_detail = (
				f"Достигнут лимит сообщений ({max_messages}) для гостевого режима. "
				f"Пожалуйста, зарегистрируйтесь, чтобы снять ограничения и продолжить диалог!"
				if is_guest else
				f"Достигнут максимальный лимит сообщений ({max_messages}) для одного диалога. "
				f"Пожалуйста, начните новый чат."
			)
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail=error_detail
			)

		self._repository.add_message(conversation_id, "user", message)
		await self._summary_service.refresh_summary(conversation_id)

		updated_message_count = self._repository.count_messages(conversation_id)
		messages = self._repository.load_prompt_messages(conversation_id)
		reply = await self._orchestrator.generate_reply(
			messages=messages,
			max_tokens=max_response_tokens,
			token=token,
			is_guest=is_guest,
			current_message_count=updated_message_count,
			max_messages=max_messages
		)

		self._repository.add_message(conversation_id, "assistant", reply)
		await self._summary_service.refresh_summary(conversation_id)

		return reply, conversation_id

	async def get_user_conversations(self, user_id: str):
		return self._repository.list_conversations(user_id)

	async def get_conversation_history(self, user_id: str, conversation_id: str) -> List[dict]:
		conversation = self._repository.get_conversation(conversation_id)
		if not conversation:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Диалог не найден")

		if conversation.user_id != user_id:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ к чужому диалогу запрещен")

		return self._repository.load_messages(conversation_id)

	async def delete_user_conversation(self, user_id: str, conversation_id: str) -> None:
		conversation = self._repository.get_conversation(conversation_id)
		if not conversation:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Диалог не найден")

		if conversation.user_id != user_id:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Удаление чужого диалога запрещено")

		self._repository.delete_conversation(conversation_id)

	async def delete_all_user_conversations(self, user_id: str) -> None:
		"""
		Находит все диалоги пользователя и удаляет их пакетно.
		"""
		conversations = self._repository.list_conversations(user_id)
		for conversation in conversations:
			self._repository.delete_conversation(conversation.id)
from app.llm.orchestrator import LLMOrchestrator
from app.repositoriy.conversation_repository_protocol import ConversationRepository
from app.repositoriy.sql_conversation_repository import SqlConversationRepository
from app.repositoriy.InMemoryConversationRepository import InMemoryConversationRepository
from app.service.summaryService import SummaryService


class ChatService:
	def __init__(
			self,
			repository: ConversationRepository | None = None,
			orchestrator: LLMOrchestrator | None = None,
			summary_service: SummaryService | None = None,
	) -> None:
		self._repository = repository or SqlConversationRepository()
		self._orchestrator = orchestrator or LLMOrchestrator()
		self._summary_service = summary_service or SummaryService(self._repository, self._orchestrator)

	# Handles a single incoming chat message.
	async def handle_message(self, user_id: str, message: str, conversation_id: str | None) -> tuple[str, str]:
		conversation_id = self._repository.get_or_create_conversation_id(user_id, conversation_id)
		self._repository.add_message(conversation_id, "user", message)

		await self._summary_service.refresh_summary(conversation_id)

		messages = self._repository.load_prompt_messages(conversation_id)
		reply = await self._orchestrator.generate_reply(messages)

		self._repository.add_message(conversation_id, "assistant", reply)
		await self._summary_service.refresh_summary(conversation_id)

		return reply, conversation_id

import asyncio

from app.service.chatService import ChatService
from app.repositoriy.InMemoryConversationRepository import InMemoryConversationRepository
from app.service.summaryService import SummaryService


class FakeOrchestrator:
	# Returns a deterministic reply for tests.
	async def generate_reply(self, messages: list[dict]) -> str:
		return "ok"

	# Returns a deterministic summary for tests.
	async def summarize_messages(self, previous_summary: str, batch: list[dict]) -> str:
		return (previous_summary + " | summary").strip(" |")


def test_chat_service_smoke() -> None:
	repository = InMemoryConversationRepository()
	orchestrator = FakeOrchestrator()
	summary_service = SummaryService(repository, orchestrator)
	service = ChatService(repository=repository, orchestrator=orchestrator, summary_service=summary_service)

	conversation_id = None
	for index in range(8):
		reply, conversation_id = asyncio.run(
			service.handle_message("user-1", f"message-{index}", conversation_id)
		)
		assert reply == "ok"
		assert conversation_id

	assert repository.get_summary(conversation_id)

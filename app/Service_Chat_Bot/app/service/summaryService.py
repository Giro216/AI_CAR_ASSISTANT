from app.llm.orchestrator import LLMOrchestrator
from app.repositoriy.conversation_repository import InMemoryConversationRepository


class SummaryService:
	def __init__(self, repository: InMemoryConversationRepository, orchestrator: LLMOrchestrator) -> None:
		self._repository = repository
		self._orchestrator = orchestrator

	# Refreshes summary while unsummarized messages exceed the hot context limit.
	async def refresh_summary(self, conversation_id: str) -> None:
		while True:
			batch = self._repository.get_next_summary_batch(conversation_id)
			if not batch:
				break
			previous_summary = self._repository.get_summary(conversation_id)
			batch_payload = [{"role": item.role, "content": item.content} for item in batch]
			new_summary = await self._orchestrator.summarize_messages(previous_summary, batch_payload)
			self._repository.advance_summary(conversation_id, new_summary, batch_size=len(batch))

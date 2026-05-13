from fastapi import APIRouter

from app.llm.orchestrator import ChatOrchestrator
from app.schema.chatMessage import ChatMessageIn, ChatMessageOut
from app.repositoriy.conversation_repository import InMemoryConversationRepository

router = APIRouter()

orchestrator = ChatOrchestrator()
repository = InMemoryConversationRepository()


# Refreshes summary while unsummarized messages exceed the hot context limit.
async def _refresh_summary(conversation_id: str) -> None:
	while True:
		batch = repository.get_next_summary_batch(conversation_id)
		if not batch:
			break
		previous_summary = repository.get_summary(conversation_id)
		batch_payload = [{"role": item.role, "content": item.content} for item in batch]
		new_summary = await orchestrator.summarize_messages(previous_summary, batch_payload)
		repository.advance_summary(conversation_id, new_summary, batch_size=len(batch))


@router.post("/message", response_model=ChatMessageOut)
async def send_message(payload: ChatMessageIn):

	conversation_id = repository.get_or_create_conversation_id(
		payload.user_id,
		payload.conversation_id,
	)
	repository.add_message(conversation_id, "user", payload.message)

	await _refresh_summary(conversation_id)

	messages = repository.load_prompt_messages(conversation_id)

	reply = await orchestrator.generate_reply(messages)

	repository.add_message(conversation_id, "assistant", reply)

	await _refresh_summary(conversation_id)

	return ChatMessageOut(reply=reply, conversation_id=conversation_id)

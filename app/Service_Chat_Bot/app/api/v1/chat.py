from fastapi import APIRouter

from app.api.v1.schemas.chat_message import ChatMessageIn, ChatMessageOut
from app.service.chatService import ChatService

router = APIRouter()

chat_service = ChatService()


@router.post("/message", response_model=ChatMessageOut)
async def send_message(payload: ChatMessageIn):
	reply, conversation_id = await chat_service.handle_message(
		user_id=payload.user_id,
		message=payload.message,
		conversation_id=payload.conversation_id,
	)

	return ChatMessageOut(reply=reply, conversation_id=conversation_id)

# TODO сделать руты для отправки истории диалогов
# app/api/v1/chat.py
from typing import List
from fastapi import APIRouter, Depends, status

from app.api.v1.schemas.chat_message import ChatMessageIn, ChatMessageOut, ConversationOut, HistoryMessageOut
from app.core.auth import UserCredentials, get_current_user_credentials
from app.core.dependency import get_chat_service
from app.service.chatService import ChatService

router = APIRouter()

@router.post("/message", response_model=ChatMessageOut)
async def send_message(
	payload: ChatMessageIn,
	current_user: UserCredentials = Depends(get_current_user_credentials),
	service: ChatService = Depends(get_chat_service),
):
	reply, conversation_id = await service.handle_message(
		user_id=str(current_user.id),
		message=payload.message,
		conversation_id=payload.conversation_id,
	)
	return ChatMessageOut(reply=reply, conversation_id=conversation_id)


@router.get("/conversations", response_model=List[ConversationOut])
async def get_my_conversations(
	current_user: UserCredentials = Depends(get_current_user_credentials),
	service: ChatService = Depends(get_chat_service),
):
	return await service.get_user_conversations(user_id=str(current_user.id))


@router.get("/conversations/{conversation_id}/history", response_model=List[HistoryMessageOut])
async def get_conversation_history(
	conversation_id: str,
	current_user: UserCredentials = Depends(get_current_user_credentials),
	service: ChatService = Depends(get_chat_service),
):
	return await service.get_conversation_history(user_id=str(current_user.id), conversation_id=conversation_id)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(
	conversation_id: str,
	current_user: UserCredentials = Depends(get_current_user_credentials),
	service: ChatService = Depends(get_chat_service),
):
	await service.delete_user_conversation(user_id=str(current_user.id), conversation_id=conversation_id)
	return {"detail": "Диалог и вся история переписки успешно удалены"}
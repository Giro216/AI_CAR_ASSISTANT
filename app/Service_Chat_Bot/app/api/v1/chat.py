from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException

from app.api.v1.schemas.chat_message import ChatMessageIn, ChatMessageOut, ConversationOut, HistoryMessageOut
from app.core.auth import UserCredentials, get_optional_user_credentials
from app.core.dependency import get_chat_service
from app.service.chatService import ChatService

router = APIRouter()

@router.post("/message", response_model=ChatMessageOut)
async def send_message(
	payload: ChatMessageIn,
	current_user: Optional[UserCredentials] = Depends(get_optional_user_credentials),
	service: ChatService = Depends(get_chat_service),
):
	# Определяем user_id: приоритет у JWT, если его нет - берем присланный фронтендом гостевой ID
	resolved_user_id = None
	if current_user:
		resolved_user_id = str(current_user.id)
	elif payload.user_id:
		resolved_user_id = payload.user_id
	else:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="user_id обязателен для неавторизованных гостевых сессий"
		)

	reply, conversation_id = await service.handle_message(
		user_id=resolved_user_id,
		message=payload.message,
		conversation_id=payload.conversation_id,
	)
	return ChatMessageOut(reply=reply, conversation_id=conversation_id)


@router.get("/conversations", response_model=List[ConversationOut])
async def get_my_conversations(
	user_id: Optional[str] = Query(None, description="Гостевой user_id для неавторизованных"),
	current_user: Optional[UserCredentials] = Depends(get_optional_user_credentials),
	service: ChatService = Depends(get_chat_service),
):
	resolved_user_id = str(current_user.id) if current_user else user_id
	if not resolved_user_id:
		raise HTTPException(status_code=400, detail="Параметр user_id или токен авторизации обязателен")
		
	return await service.get_user_conversations(user_id=resolved_user_id)


@router.get("/conversations/{conversation_id}/history", response_model=List[HistoryMessageOut])
async def get_conversation_history(
	conversation_id: str,
	user_id: Optional[str] = Query(None, description="Гостевой user_id для неавторизованных"),
	current_user: Optional[UserCredentials] = Depends(get_optional_user_credentials),
	service: ChatService = Depends(get_chat_service),
):
	resolved_user_id = str(current_user.id) if current_user else user_id
	if not resolved_user_id:
		raise HTTPException(status_code=400, detail="Параметр user_id или токен авторизации обязателен")
		
	return await service.get_conversation_history(user_id=resolved_user_id, conversation_id=conversation_id)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(
	conversation_id: str,
	user_id: Optional[str] = Query(None, description="Гостевой user_id для неавторизованных"),
	current_user: Optional[UserCredentials] = Depends(get_optional_user_credentials),
	service: ChatService = Depends(get_chat_service),
):
	"""
	Удалить диалог и всю историю переписки.
	"""
	resolved_user_id = str(current_user.id) if current_user else user_id
	if not resolved_user_id:
		raise HTTPException(status_code=400, detail="Параметр user_id или токен авторизации обязателен")
		
	await service.delete_user_conversation(user_id=resolved_user_id, conversation_id=conversation_id)
	return {"detail": "Диалог и вся история переписки гостя успешно удалены"}
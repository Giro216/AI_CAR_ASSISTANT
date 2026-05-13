from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    user_id: str
    message: str
    conversation_id: str | None = None


class ChatMessageOut(BaseModel):
    reply: str
    conversation_id: str | None = None


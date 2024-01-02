from pydantic import BaseModel


class ChatMessage(BaseModel):
    id: int
    content: str


class Thumbnail(BaseModel):
    id: int
    text: str


class ChatHistoryMessage(BaseModel):
    message_counter: int
    message_text: str
    message_type: str

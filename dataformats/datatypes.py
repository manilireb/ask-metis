from pydantic import BaseModel


class ChatMessage(BaseModel):
    id: int
    content: str


class Thumbnail(BaseModel):
    id: int
    text: str

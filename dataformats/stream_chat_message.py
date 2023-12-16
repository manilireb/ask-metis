from pydantic import BaseModel


class StreamChatMessage(BaseModel):
    content: str

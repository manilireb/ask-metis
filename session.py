from typing import List

from pydantic import BaseModel

from chatmodels import ChatModel


class Session(BaseModel):
    id: str
    chatmodel: ChatModel = ChatModel(streaming=True)
    history: List[str] = []

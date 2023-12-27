from pydantic import BaseModel


class Thumbnail(BaseModel):
    id: int
    text: str

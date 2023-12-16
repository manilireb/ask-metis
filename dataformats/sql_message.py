from typing import Optional

from sqlmodel import Field, SQLModel


class SQLMessage(SQLModel, table=True):
    session_id: int = Field(primary_key=True, nullable=False)
    session_idx: int = Field(primary_key=True, nullable=False)
    session_message: Optional[str]
    message_type: str = Field(nullable=False)

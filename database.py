from typing import Optional

from sqlmodel import Field, SQLModel, create_engine

from env import env

engine = create_engine(f"sqlite:///{env.db_file}")


class SQLMessage(SQLModel, table=True):
    session_id: int = Field(primary_key=True, nullable=False)
    session_idx: int = Field(primary_key=True, nullable=False)
    session_message: Optional[str]
    message_type: str = Field(nullable=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

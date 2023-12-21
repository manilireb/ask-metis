from typing import List

from sqlalchemy.engine.base import Engine
from sqlmodel import Session as DBSession
from sqlmodel import select

from chatmodels import ChatModel
from database import SQLMessage
from dataformats import ChatMessage


class Session:
    def __init__(self, id: int, engine: Engine):
        self._id: int = id
        self._engine: Engine = engine
        self._chatmodel: ChatModel = ChatModel(streaming=True)
        self._history: List[str] = []
        self._message_counter: int = 0

    def get_chat_model_generator(self, message: ChatMessage):
        generator = self._chatmodel.get_generator(message.content)
        self.insert_into_db(message_text=message.content, message_type="Human")
        return generator

    def load_from_db(self):
        with DBSession(self._engine) as db_session:
            statement = select(SQLMessage).where(SQLMessage.session_id == self._id)
            results = sorted(
                db_session.exec(statement).all(), key=lambda x: x.session_idx
            )
            for res in results:
                self._history.append(
                    (res.session_idx, res.session_message, res.message_type)
                )
                self._chatmodel.insert_into_memory(
                    message=res.session_message, message_type=res.message_type
                )
            self._message_counter = len(self._history)

    def insert_into_db(self, message_text: str, message_type: str):
        message = SQLMessage(
            session_id=self._id,
            session_idx=self._message_counter,
            session_message=message_text,
            message_type=message_type,
        )
        with DBSession(self._engine) as db_session:
            db_session.add(message)
            db_session.commit()

        self._history.append((self._message_counter, message_text, message_type))
        self._message_counter = len(self._history)

    def get_request_cost(self):
        return self._chatmodel.get_request_cost()


if __name__ == "__main__":
    from database import create_db_and_tables, engine

    create_db_and_tables()
    session = Session(id=15, engine=engine)
    session.load_from_db()
    print(session._history)

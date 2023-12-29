import random
from typing import List, Set

from cachetools import TTLCache, cached
from sqlalchemy.engine.base import Engine
from sqlmodel import Session as DBSession
from sqlmodel import delete, select

from database import SQLMessage
from dataformats import Thumbnail
from env import env
from exceptions import SessionHandlerException
from sessions import Session

session_cache = TTLCache(maxsize=env.cache_size, ttl=env.ttl)


class SessionHandler:
    def __init__(self, engine: Engine):
        self._engine = engine
        self._ids = self._load_ids()

    def create_session(self) -> int:
        if len(self._ids) > env.max_n_sessions:
            raise SessionHandlerException(
                "No more available space for storing sessions."
            )
        id = self._get_random_id()
        session = Session(id=id, engine=self._engine)
        session_cache[id] = session
        self._ids.add(id)
        return id

    @cached(session_cache)
    def get_session(self, id: int) -> Session:
        if id not in self._ids:
            raise SessionHandlerException("Id does not exist")
        session = Session(id=id, engine=self._engine)
        session.load_from_db()
        return session

    def load_thumbnails(self) -> List[Thumbnail]:
        with DBSession(self._engine) as db_session:
            statement = select(SQLMessage.session_id, SQLMessage.session_message).where(
                SQLMessage.session_idx == 0
            )
            response = db_session.exec(statement).all()
            return [Thumbnail(id=x[0], text=x[1]) for x in response]

    def delete_session(self, id: int) -> None:
        with DBSession(self._engine) as db_session:
            statement = delete(SQLMessage).where(SQLMessage.session_id == id)
            db_session.exec(statement)
            db_session.commit()

    def _load_ids(self) -> Set[int]:
        with DBSession(self._engine) as db_session:
            statement = select(SQLMessage.session_id)
            return set(db_session.exec(statement).all())

    def _get_random_id(self) -> int:
        random_id = random.randint(1, env.max_n_sessions)
        while random_id in self._ids:
            random_id = random.randint(0, env.max_n_sessions)
        return random_id

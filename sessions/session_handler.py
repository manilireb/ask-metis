import random
from typing import Set

from sqlalchemy.engine.base import Engine
from sqlmodel import Session as DBSession
from sqlmodel import select

from database import SQLMessage
from env import env
from exceptions import SessionHandlerException
from sessions import Session


class SessionHandler:
    def __init__(self, engine: Engine):
        self._engine = engine
        self._ids = self._load_ids()
        self._session_cache = dict()

    def create_session(self) -> int:
        id = self._get_random_id()
        session = Session(id=id, engine=self._engine)
        self._session_cache[id] = session
        self._ids.add(id)
        return id

    def get_session(self, id: int) -> Session:
        if id not in self._ids:
            raise SessionHandlerException("Id does not exist")
        if id not in self._session_cache.keys():
            session = Session(id=id, engine=self._engine)
            session.load_from_db()
            self._session_cache[id] = session
            return session
        return self._session_cache[id]

    def get_ids(self) -> Set[int]:
        return self._ids

    def _load_ids(self) -> Set[int]:
        with DBSession(self._engine) as db_session:
            statement = select(SQLMessage.session_id)
            return set(db_session.exec(statement).all())

    def _get_random_id(self) -> int:
        random_id = random.randint(0, env.max_n_sessions)
        while random_id in self._ids:
            random_id = random.randint(0, env.max_n_sessions)
        return random_id

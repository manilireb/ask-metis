import os

from pydantic import BaseModel


class Env(BaseModel):
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-4-1106-preview")
    chat_history_size: int = os.getenv("CHAT_HISTORY_SIZE", 5)
    db_file: str = os.getenv("DB_FILE", "database.db")
    temperature: float = os.getenv("LLM_TEMPERATURE", 0.3)
    max_n_sessions: int = os.getenv("MAX_N_SESSIONS", 100)
    cache_size: int = os.getenv("CACHE_SIZE", 100)
    ttl: int = os.getenv("TTL", 600)


env = Env()

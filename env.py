import os

from pydantic import BaseModel


class Env(BaseModel):
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-4-1106-preview")
    chat_history_size: int = os.getenv("CHAT_HISTORY_SIZE", 5)
    db_file: str = os.getenv("DB_FILE", "database.db")


env = Env()

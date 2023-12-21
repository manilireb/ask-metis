from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from database import create_db_and_tables, engine
from dataformats import ChatMessage
from sessions import SessionHandler

app = FastAPI()
create_db_and_tables()
session_handler = SessionHandler(engine)


@app.get("/")
def sanity_check():
    return 200


@app.get("/stream_chat/")
async def stream_chat(message: ChatMessage):
    session = session_handler.get_session(message.id)
    generator = session.get_chat_model_generator(message=message)
    return StreamingResponse(generator, media_type="text/event-stream")


@app.get("/total_cost")
def get_request_cost(id: int):
    session = session_handler.get_session(id)
    return {"cost": session.get_request_cost()}


@app.post("/add_to_database")
def insert_message(message: ChatMessage):
    session = session_handler.get_session(message.id)
    session.insert_into_db(message_text=message.content, message_type="AI")

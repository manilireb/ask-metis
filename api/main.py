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


@app.get("/create_new_session")
async def create_new_session():
    id = session_handler.create_session()
    return {"id": id}


@app.get("/load_existing_session")
async def load_exisiting_session(id: int):
    session = session_handler.get_session(id)
    return {"chat_history": session.get_history()}


@app.get("/get_session_thumbnails")
def get_session_thumbnails():
    thumbnails = session_handler.load_thumbnails()
    ids = [tn.id for tn in thumbnails]
    texts = [tn.text for tn in thumbnails]
    return {"ids": ids, "texts": texts}


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


@app.post("/delete_session")
def delete_session(id: int):
    session_handler.delete_session(id=id)


@app.get("/get_current_model_name")
def get_current_model_name(id: int):
    session = session_handler.get_session(id)
    return {"model_name": session.get_current_model_name()}

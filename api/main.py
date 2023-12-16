from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from database import create_db_and_tables, engine
from dataformats import StreamChatMessage
from session import Session

app = FastAPI()
create_db_and_tables()
session = Session(id=15, engine=engine)
session.load_from_db()


@app.get("/")
def sanity_check():
    return 200


@app.post("/chat")
def chat(question: str):
    answer, cost = session.chat_model.chat(question)
    return {"answer": answer, "cost": cost}


@app.get("/stream_chat/")
async def stream_chat(message: StreamChatMessage):
    generator = session.get_chat_model_generator(message=message)
    return StreamingResponse(generator, media_type="text/event-stream")


@app.get("/total_cost")
def get_request_cost():
    return {"cost": session._chatmodel.get_total_cost()}

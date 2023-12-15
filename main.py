from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from model import ChatModel

app = FastAPI()
chat_model = ChatModel(streaming=True)


class Message(BaseModel):
    content: str


@app.get("/")
def sanity_check():
    return 200


@app.post("/chat")
def chat(question: str):
    answer, cost = chat_model.chat(question)
    return {"answer": answer, "cost": cost}


@app.get("/stream_chat/")
async def stream_chat(message: Message):
    # session = SessionHandler.get_seesion(id)
    # generator = session.chat_model.get_generator(message.content)
    # return StreamingResponse(generator, media_type="text/event-stream")
    generator = chat_model.get_generator(message.content)
    return StreamingResponse(generator, media_type="text/event-stream")


@app.get("/total_cost")
def get_request_cost():
    return {"cost": chat_model.get_total_cost()}

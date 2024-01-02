import asyncio
import os
from typing import AsyncIterable, Awaitable

from dotenv import load_dotenv
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage

from callbackhandlers import TokenMetricsCallbackHandler


class ChatModel:
    def __init__(self, llm_model_name: str, chat_hisotry_size: int, temperature: float):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY1")
        self._model_name = llm_model_name
        self._chat_history_size = chat_hisotry_size
        self._temperature = temperature
        self._load_chat_model(api_key=api_key, model_name=self._model_name)
        self._configure_chat()

    def insert_into_memory(self, message: str, message_type) -> None:
        if message_type == "Human":
            self._memory.chat_memory.messages.append(HumanMessage(content=message))
        if message_type == "AI":
            self._memory.chat_memory.messages.append(AIMessage(content=message))

    async def get_generator(self, message_text: str) -> AsyncIterable[str]:
        self._callback.done.clear()

        async def wrap_done(fn: Awaitable, event: asyncio.Event):
            try:
                await fn
            except Exception as e:
                print(f"Caught exception: {e}")
            finally:
                event.set()

        task = asyncio.create_task(
            wrap_done(
                self._chain.ainvoke({"message": message_text}), self._callback.done
            )
        )
        async for token in self._callback.aiter():
            yield token

        await task

    def get_request_cost(self) -> float:
        return self._tokencounter.total_cost

    def _load_chat_model(self, api_key: str, model_name: str) -> None:
        self._callback = AsyncIteratorCallbackHandler()
        self._tokencounter = TokenMetricsCallbackHandler()
        self._llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name=model_name,
            streaming=True,
            temperature=self._temperature,
            callbacks=[self._callback, self._tokencounter],
        )
        self._memory = ConversationBufferWindowMemory(
            memory_key="chat_history", return_messages=True, k=self._chat_history_size
        )

    def _configure_chat(self) -> None:
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    "You are a helpful assistant that chats with the user. Always respond concise and polite."
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{message}"),
            ]
        )
        self._chain = LLMChain(
            llm=self._llm,
            prompt=prompt,
            memory=self._memory,
        )

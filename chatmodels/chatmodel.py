import asyncio
import os
from typing import AsyncIterable, Awaitable, Dict, List

import requests
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
from exceptions import ChatModelException

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY1")


class ChatModel:
    def __init__(self, llm_model_name: str, chat_hisotry_size: int, temperature: float):
        self._model_name = llm_model_name
        self._chat_history_size = chat_hisotry_size
        self._temperature = temperature
        self._load_chat_model(api_key=API_KEY, model_name=self._model_name)
        self._configure_chat()

    def insert_into_memory(self, message: str, message_type) -> None:
        if message_type == "Human":
            self._memory.chat_memory.messages.append(HumanMessage(content=message))
        if message_type == "AI":
            self._memory.chat_memory.messages.append(AIMessage(content=message))

    async def get_generator(self, message_text: str) -> AsyncIterable[str]:
        self._callback.done.clear()
        model_type = self._select_model(message_text=message_text)
        chain = self._select_chain(model_type=model_type)

        async def wrap_done(fn: Awaitable, event: asyncio.Event):
            try:
                await fn
            except Exception as e:
                print(f"Caught exception: {e}")
            finally:
                event.set()

        task = asyncio.create_task(
            wrap_done(chain.ainvoke({"message": message_text}), self._callback.done)
        )
        async for token in self._callback.aiter():
            yield token

        await task

    def get_request_cost(self) -> float:
        if self._current_model_name == "gpt-3.5":
            return self._tokencounter3.total_cost
        elif self._current_model_name == "gpt-4":
            return self._tokencounter4.total_cost
        else:
            raise ChatModelException("Invalid chat model name")

    def get_current_model_name(self):
        return self._current_model_name

    def _load_chat_model(self, api_key: str, model_name: str) -> None:
        self._callback = AsyncIteratorCallbackHandler()
        self._tokencounter4 = TokenMetricsCallbackHandler(
            model_name="gpt-4-1106-preview"
        )
        self._llm4 = ChatOpenAI(
            openai_api_key=api_key,
            model_name="gpt-4-1106-preview",
            streaming=True,
            temperature=self._temperature,
            callbacks=[self._callback, self._tokencounter4],
        )
        self._tokencounter3 = TokenMetricsCallbackHandler(model_name="gpt-3.5-turbo")
        self._llm3 = ChatOpenAI(
            openai_api_key=api_key,
            model_name="gpt-3.5-turbo",
            streaming=True,
            temperature=self._temperature,
            callbacks=[self._callback, self._tokencounter3],
        )

        self._memory = ConversationBufferWindowMemory(
            memory_key="chat_history", return_messages=True, k=self._chat_history_size
        )

    def _select_model(self, message_text: str) -> str:
        url = "https://not-diamond-backend.onrender.com/modelSelector/"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {os.environ.get('NOT_DIAMOND_API_KEY')}",
            "content-type": "application/json",
        }

        payload = {
            "messages": self._transform_memory()
            + [{"role": "user", "content": message_text}]
        }

        return requests.post(url, json=payload, headers=headers).json()["model"]

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
        self._current_model_name = "gpt-4"
        self._chain4 = LLMChain(llm=self._llm4, prompt=prompt, memory=self._memory)
        self._chain3 = LLMChain(llm=self._llm3, prompt=prompt, memory=self._memory)

    def _select_chain(self, model_type: str):
        if model_type == "gpt-3.5":
            self._current_model_name = "gpt-3.5"
            return self._chain3
        elif model_type == "gpt-4":
            self._current_model_name = "gpt-4"
            return self._chain4
        else:
            raise ChatModelException(
                "Modelname {model_type} is invalid. Must be either gpt-3.5 or gpt-4."
            )

    def _transform_memory(self) -> List[Dict[str, str]]:
        base_messages = self._memory.chat_memory.messages
        return [
            {"role": message.type, "content": message.content}
            for message in base_messages
        ]

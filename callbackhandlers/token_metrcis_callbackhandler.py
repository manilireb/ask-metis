from typing import Any, Dict, List

import tiktoken
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.openai_info import (
    get_openai_token_cost_for_model,
    standardize_model_name,
)
from tiktoken.core import Encoding


class TokenMetricsCallbackHandler(BaseCallbackHandler):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.enc: Encoding = tiktoken.encoding_for_model(self.model_name)
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_cost: int = 0.0

    def __repr__(self) -> str:
        return (
            f"Tokens Used: {self.prompt_tokens + self.completion_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Total Cost (USD): ${self.total_cost:f}\n"
        )

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        self.prompt_tokens = len(self.enc.encode(prompts[0]))

    async def on_llm_new_token(self, token: str, **kwargs):
        self.completion_tokens += 1

    async def on_llm_end(self, response, **kwargs: Any) -> None:
        model_name = standardize_model_name(self.model_name, "")
        prompt_cost = get_openai_token_cost_for_model(model_name, self.prompt_tokens)
        completion_cost = get_openai_token_cost_for_model(
            model_name, self.completion_tokens, is_completion=True
        )
        self.total_cost = prompt_cost + completion_cost

        # Reset completion tokens
        self.completion_tokens = 0

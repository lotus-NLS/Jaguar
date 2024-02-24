from __future__ import annotations

import json, tiktoken
from typing import Optional
from tiktoken import Encoding
from abc import abstractmethod

from enum import Enum
from hollarek.tmpl import Loggable
from .generation import Generation, Options, Context

# ---------------------------------------------------------

class ModelType(Enum):
    pass

class LLM(Loggable):
    def __init__(self, model: ModelType):
        super().__init__()
        self.model_type : str = model.value
        self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(self.model_type))

    @abstractmethod
    def get_generation(self, context : Context, options: Options) -> Generation:
        pass


class Tokenizer(Loggable):
    def __init__(self, encoding : Encoding):
        super().__init__()
        self.encoding : encoding = encoding


    def get_token_count(self, the_str: str) -> int:
        return len(self.encode(the_str))


    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        encoded_str = self.encode(the_str)
        return self.decode(encoded_str[:max_tokens])

    def get_tokens(self, context : Context) -> Optional[int]:
        try:
            token_count = 0
            tool_docs = context.tool_docs
            the_tools = [] if tool_docs is None else tool_docs
            for entry in context.entries:
                token_count += self.get_token_count(the_str=f'{entry}')
            for tool_docs in the_tools:
                token_count += self.get_token_count(the_str=json.dumps(tool_docs))
        except:
            token_count = None

        return token_count


    def encode(self, text : str) -> list[int]:
        return self.encoding.encode(text=text)

    def decode(self, tokens : list[int]) -> str:
        return self.encoding.decode(tokens=tokens)

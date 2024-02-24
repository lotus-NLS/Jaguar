from __future__ import annotations

import json, tiktoken
from typing import Optional
from tiktoken import Encoding
from abc import abstractmethod

from hollarek.tmpl import Loggable
from api import Entry
from .generation import Generation, GenerationOptions


# ---------------------------------------------------------


class LLM(Loggable):
    def __init__(self, model_type: str):
        super().__init__()
        self.model_type : str = model_type
        self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(self.model_type))

    @abstractmethod
    def get_generation(self, entries: list[Entry], tool_docs: list[dict], options: GenerationOptions) -> Generation:
        pass



class Tokenizer(Loggable):
    def __init__(self, encoding : Encoding):
        super().__init__()
        self.encoding : encoding = encoding
        self.encode = encoding.encode
        self.decode = encoding.decode

    def get_token_count(self, the_str: str) -> int:
        return len(self.encode(the_str))


    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        encoded_str = self.encode(the_str)
        return self.decode(encoded_str[:max_tokens])

    def get_tokens_estimate(self, entries: list[Entry], tool_docs: Optional[list[dict]] = None) -> Optional[int]:
        try:
            token_count = 0
            the_tools = [] if tool_docs is None else tool_docs
            for entry in entries:
                token_count += self.get_token_count(the_str=f'{entry}')
            for tool_docs in the_tools:
                token_count += self.get_token_count(the_str=json.dumps(tool_docs))
        except:
            token_count = None

        return token_count

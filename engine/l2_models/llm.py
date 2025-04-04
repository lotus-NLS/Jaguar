from __future__ import annotations

import json
from abc import abstractmethod
from typing import Optional

import tiktoken
from tiktoken import Encoding

from engine.l2_models.language import Message, Context
from engine.l2_models.generation import InfConfig, Generation, CallOptions
from holytools.logging import Loggable


# ---------------------------------------------------------

class LLM(Loggable):
    def __init__(self, name : str, api_key : Optional[str] = None):
        super().__init__()
        self.api_key : str = api_key
        self._name : str = name
        self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.get_encoding(encoding_name=f'o200k_base'))

    @abstractmethod
    def get_generation(self, context : Context, options: InfConfig) -> Generation:
        pass

    def get_text_generation(self, entries: list[Message]) -> Generation:
        context = Context(entries=entries, docs=[])
        options = InfConfig(call_options=CallOptions.no_call())
        return self.get_generation(context=context, options=options)

    def check_token_cap_ok(self, context : Context, token_cap : int) -> bool:
        num_tokens = self.tokenizer.count_context_tokens(context=context)
        return num_tokens <= token_cap

class Tokenizer:
    def __init__(self, encoding : Encoding):
        super().__init__()
        self.encoding : encoding = encoding

    def count_string_tokens(self, the_str: str) -> int:
        return len(self.encode(the_str))

    def count_context_tokens(self, context : Context) -> Optional[int]:
        try:
            token_count = 0
            tool_docs = context.docs
            the_tools = [] if tool_docs is None else tool_docs
            for entry in context.entries:
                token_count += self.count_string_tokens(the_str=f'{entry}')
            for tool_docs in the_tools:
                token_count += self.count_string_tokens(the_str=json.dumps(tool_docs))
        except:
            token_count = None

        return token_count

    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        encoded_str = self.encode(the_str)
        return self.decode(encoded_str[:max_tokens])

    def encode(self, text : str) -> list[int]:
        return self.encoding.encode(text=text)

    def decode(self, tokens : list[int]) -> str:
        return self.encoding.decode(tokens=tokens)

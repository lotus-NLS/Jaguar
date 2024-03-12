from __future__ import annotations
from api import Entry

import json, tiktoken
from typing import Optional
from tiktoken import Encoding
from abc import abstractmethod
from hollarek.logging import Loggable
from .generation import Generation, Context
from .options import Options, ToolOptions
from dataclasses import dataclass

# ---------------------------------------------------------

@dataclass
class ModelInfo:
    name : str
    supports_vision : bool
    supports_tools : bool = True


class LLM(Loggable):
    def __init__(self, model_info: ModelInfo):
        super().__init__()
        self.model_type : ModelInfo = model_info
        self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(self.get_model_name()))

    def get_model_name(self) -> str:
        return self.model_type.name

    def supports_vision(self) -> bool:
        return self.model_type.supports_vision

    def supports_tool_calls(self) -> bool:
        return self.model_type.supports_tools

    @abstractmethod
    def get_generation(self, context : Context, options: Options) -> Generation:
        pass

    def get_text_generation(self, entries: list[Entry]) -> Generation:
        context = Context(entries=entries, docs=[])
        options = Options(tool_options=ToolOptions.no_call())
        return self.get_generation(context=context, options=options)


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
            tool_docs = context.docs
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

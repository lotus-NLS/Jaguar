from __future__ import annotations

import json
import tiktoken
from abc import abstractmethod
from typing import Optional

from tiktoken import Encoding

from api import Entry
from engine.l2_models.generation import Options, Generation, CallOptions, Context
from holytools.logging import Loggable


# ---------------------------------------------------------

class LLM(Loggable):
    def __init__(self, name : str, token_cap : int = 8192):
        super().__init__()
        self._name : str = name
        self.token_cap : int = token_cap

        # TODO: This is a workaround pending issue https://github.com/openai/tiktoken/issues/367
        name = name if not name == 'o1' else 'o1-'
        self.tokenizer: Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(name))
        # self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(self._name))


    @abstractmethod
    def get_generation(self, context : Context, options: Options) -> Generation:
        pass

    def get_text_generation(self, entries: list[Entry]) -> Generation:
        context = Context(entries=entries, docs=[])
        options = Options(call_options=CallOptions.no_call())
        return self.get_generation(context=context, options=options)

    def get_name(self) -> str:
        return self._name

    def check_token_cap(self, context : Context):
        num_tokens = self.tokenizer.count_context_tokens(context=context)
        if num_tokens > self.token_cap:
            raise ValueError(f'Token cap exceeded: {num_tokens} > {self.token_cap}')



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

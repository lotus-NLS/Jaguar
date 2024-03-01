from __future__ import annotations


from api import Entry
import json, tiktoken
from typing import Optional
from tiktoken import Encoding
from abc import abstractmethod

from enum import Enum
from hollarek.dev.log import Loggable
from .generation import Generation, Options, GenerationContext, ToolOptions
# ---------------------------------------------------------

class ModelType(Enum):
    pass


class LLM:
    def __init__(self, model_type: ModelType):
        super().__init__()
        self.model_type : str = model_type.value
        self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(self.model_type))

    @abstractmethod
    def get_generation(self, context : GenerationContext, options: Options) -> Generation:
        pass

    def get_text_generation(self, entries : list[Entry]) -> Generation:
        context = GenerationContext(entries=entries, docs=[])
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

    def get_tokens(self, context : GenerationContext) -> Optional[int]:
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

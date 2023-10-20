import tiktoken
from tiktoken import Encoding
from abc import abstractmethod
from src.l3_lotus_core import Entry

from .actionstream import ActionStream, ActionOptions

# ---------------------------------------------------------


class LLM:
    def __init__(self, model_type: str):
        self.model_type : str = model_type
        self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(self.model_type))

    @abstractmethod
    def get_action_stream(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> ActionStream:
        pass


    def get_string_tokens(self, the_str: str) -> int:
        return self.tokenizer.get_string_tokens(the_str=the_str)


    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        return self.tokenizer.get_limited_string(the_str=the_str,max_tokens=max_tokens)



class Tokenizer:
    def __init__(self, encoding : Encoding):
        self.encoding : encoding = encoding
        self.encode = encoding.encode
        self.decode = encoding.decode

    def get_string_tokens(self, the_str : str) -> int:
        return len(self.encode(the_str))


    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        encoded_str = self.encode(the_str)
        return self.decode(encoded_str[:max_tokens])

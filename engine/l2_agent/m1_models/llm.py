import json
import tiktoken, logging
from typing import Optional
from tiktoken import Encoding
from abc import abstractmethod
from api import Entry

from .actionstream import ActionStream
from .options import ActionOptions
# ---------------------------------------------------------


class LLM:
    def __init__(self, model_type: str):
        self.model_type : str = model_type
        self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(self.model_type))
        self.show_debug : bool = False


    def enable_debugging(self):
        self.show_debug = True

    @abstractmethod
    def get_action_stream(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> ActionStream:
        pass


    def get_num_tokens(self, the_str: str) -> int:
        return self.tokenizer.get_string_tokens(the_str=the_str)


    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        return self.tokenizer.get_limited_string(the_str=the_str,max_tokens=max_tokens)

    # Accurate up to ~10%
    def get_tokens_estimate(self, entries: list[Entry], tool_docs: Optional[list[dict]] = None) -> Optional[int]:
        try:
            token_count = 0
            the_tools = [] if tool_docs is None else tool_docs
            for entry in entries:
                token_count += self.get_num_tokens(the_str=f'{entry}')
            for tool_docs in the_tools:
                token_count += self.get_num_tokens(the_str=json.dumps(tool_docs))
            return token_count

        except Exception as e:
            logging.error(f'Failed to estimate token count: {e}')
            return None


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


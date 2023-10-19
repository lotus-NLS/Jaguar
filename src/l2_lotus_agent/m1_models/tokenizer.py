# from typing import Optional
from tiktoken import Encoding
# from src.l3_lotus_core import Entry

# ---------------------------------------------------------

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

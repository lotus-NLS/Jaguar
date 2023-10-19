import tiktoken
from tiktoken import Encoding
from abc import abstractmethod
from src.l3_lotus_core import Entry

from src.l2_lotus_agent.m2_action.action import Action
from src.l2_lotus_agent.m2_action.action_options import ActionOptions
from .tokenizer import Tokenizer
# ---------------------------------------------------------



class LLM:
    def __init__(self, model_type: str):
        self._model_type : str = model_type
        self.tokenizer : Tokenizer = Tokenizer(encoding=tiktoken.encoding_for_model(self._model_type))

    @abstractmethod
    def get_action(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
        pass


    def get_string_tokens(self, the_str: str) -> int:
        return self.tokenizer.get_string_tokens(the_str=the_str)


    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        return self.tokenizer.get_limited_string(the_str=the_str,max_tokens=max_tokens)
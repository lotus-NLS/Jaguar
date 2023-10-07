from tiktoken import Encoding
from abc import abstractmethod
from src.l3_lotus_core import Entry

from src.l2_lotus_agent.m1_models.action import Action, ActionOptions
from src.l2_lotus_agent.m1_models.tokenizer import Tokenizer
# ---------------------------------------------------------



class LLM:
    def __init__(self, model_type: str, encoding : Encoding):
        self._model_type : str = model_type
        self.tokenizer : Tokenizer = Tokenizer(encoding=encoding)

    @abstractmethod
    def get_action(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
        pass


    def get_token_count(self,the_str: str) -> int:
        return self.tokenizer.get_string_tokens(the_str=the_str)


    def get_limited_string(self, the_str : str, max_tokens : int) -> str:
        encoded_str = self.tokenizer.encode(the_str)
        return self.tokenizer.decode(encoded_str[:max_tokens])

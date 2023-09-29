from typing import Optional
from src.l2_lotus_core.m1_models import Action, ActionOptions
from src.l2_lotus_core.m2_conversation import ConversationEntry

# ---------------------------------------------------------

class FunctionCallModes:
    auto = 'auto'
    none = 'none'


class LLM:
    def __init__(self, model_type: str):
        self._model_type : str = model_type

    def get_action(self, entries: list[ConversationEntry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
        pass


    def get_limited_string(self, the_str : str, max_tokens : int):
        pass

    def get_token_count(self,the_str: str) -> int:
        pass

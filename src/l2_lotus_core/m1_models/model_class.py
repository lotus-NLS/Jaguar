from src.l2_lotus_core.m1_models import Action, ActionOptions
from src.l2_lotus_core.m2_conversation import ConversationEntry

# ---------------------------------------------------------

class FunctionCallModes:
    auto = 'auto'
    none = 'none'

class Context:
    def __init__(self, tool_docs : list[dict], msg_history : list[ConversationEntry]):
        self.tool_docs : list[dict] = tool_docs
        self.msg_history : list[ConversationEntry] = msg_history


class LLM:
    def __init__(self,name : str):
        self.name = name

    def get_next_action(self, context : Context, action_options : ActionOptions) -> Action:
        pass


    def get_limited_string(self, the_str : str, max_tokens : int):
        pass

    def get_token_count(self,the_str: str) -> int:
        pass

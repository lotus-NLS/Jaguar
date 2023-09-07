from src.l2_lotus_core.m1_models.actioncontent import ActionContent, ActionOptions
from src.l2_lotus_core.m1_conversation.conversation_participant import ConversationEntry
from src.l2_lotus_core.m0_agent.tool import ToolInstruction

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

    def get_next_action(self, context : Context, action_options : ActionOptions) -> ActionContent:
        pass
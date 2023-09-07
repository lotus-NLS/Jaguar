from typing import Optional
from src.l2_lotus_core.agent.action import Action
from src.l2_lotus_core.conversation.conversation_participant import ConversationEntry

# ---------------------------------------------------------

class FunctionCallModes:
    auto = 'auto'
    none = 'none'

class LLM:
    def __init__(self,name : str):
        self.name = name

    # TODO: It's probably better to consolidate this into one or two arguments, like context and options
    def get_next_action(self
                        , msg_history : list[ConversationEntry]
                        , tool_instructions : object
                        , is_allowed_functioncall : bool = True
                        , max_tokens : Optional[int] = None
                        , temperature : float = 0.3) -> Action:
        pass
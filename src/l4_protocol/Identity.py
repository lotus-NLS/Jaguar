from src.l4_conversation.l0_conversation_participant import DialogueRole
from src.l4_conversation.l2_conversation_entry import ConversationEntry


# ----------------------------------------------------


class Identity:
    def __init__(self,core : str, principles : str):
        self.core : str = core
        self.principles : str = principles

    def get_msg(self):
        core_msg = f'{self.core}\n'
        principles_msg = f'{self.principles}\n'

        return ConversationEntry(role=DialogueRole.system(), msg=core_msg + principles_msg)
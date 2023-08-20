from s1_conversation.Conversation import Conversation_Entry, Dialogue_Roles


# ----------------------------------------------------


class Identity:
    def __init__(self,core : str, principles : str):
        self.core : str = core
        self.principles : str = principles

    def get_msg(self):
        core_msg = f'{self.core}\n'
        principles_msg = f'{self.principles}\n'

        return Conversation_Entry(role=Dialogue_Roles.system, msg=core_msg+principles_msg)
from s1_conversation.Conversation import Conversation_Entry, Dialogue_Roles


# ----------------------------------------------------


class Identity:
    def __init__(self,core,principles):
        self.core : str = core
        self.principles_list : list[str] = principles

    def get_system_message(self):
        core_msg = f'{self.core}\n'
        principles_msg = ''
        for principle in self.principles_list:
            principles_msg += f'{principle}\n'

        return Conversation_Entry(role=Dialogue_Roles.system, msg=core_msg+principles_msg)
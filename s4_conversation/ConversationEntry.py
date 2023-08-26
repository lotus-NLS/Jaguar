from s4_conversation.DialogueRoles import DialogueRole


class ConversationEntry(dict):
    def __init__(self,role : DialogueRole, msg : str):
        super().__init__()
        self['role'] = role
        self['content'] = msg

    def get_role(self):
        return self['role']

    def get_content(self):
        return self['content']
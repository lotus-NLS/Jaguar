from s4_conversation.s3_DialogueRoles import DialogueRole


class ConversationEntry(dict):
    def __init__(self, role : DialogueRole, msg : str, tool_name ='undefined_function'):
        super().__init__()
        self['role'] = role
        self['content'] = msg
        if role == DialogueRole.tool():
            self['name'] = tool_name

    def get_role(self):
        return self['role']

    def get_content(self):
        return self['content']
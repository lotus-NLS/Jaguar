from s1_conversation.Conversation import Dialogue_Roles


# ---------------------------------------------------------

class Conversation_Entry(dict):
    def __init__(self,role : str, msg : str):
        super().__init__()

        if not role in Dialogue_Roles.as_list():
            print(f'[Debug]: Given role {role} is not part of the allowed roles {Dialogue_Roles.as_list()}. Defaulting to agent role ...')
            self['role'] = Dialogue_Roles.agent
        else:
            self['role'] = role

        if not isinstance(msg,str):
            print(f'[Debug]: Given message {msg} is not a string. Typecasting msg object to string to include as message content ...')
            self['content'] = str(msg)

        else:
            self['content'] = msg


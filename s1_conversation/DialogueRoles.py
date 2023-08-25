class DialogueRole(str):
    user = 'user'
    agent = 'assistant'
    system = 'system'

    def __new__(cls, role : str):
        if not role in DialogueRole.as_list():
            print(f'[Debug]: Given role {role} is not part of the allowed roles {DialogueRole.as_list()}. Defaulting to agent role ...')
            return DialogueRole.agent

        else:
            return role

    @classmethod
    def as_list(cls):
        as_list = []
        for name, value in cls.__dict__.items():
            if not name.startswith("__"):
                as_list.append(value)
        return as_list
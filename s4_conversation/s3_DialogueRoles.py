
class DialogueRole(str):
    _m_user = 'user'
    _m_agent = 'assistant'
    _m_system = 'system'
    _m_tool = 'function'

    def __new__(cls, role : str):
        if not role in DialogueRole.__as_list__():
            print(f'[Debug]: Given role {role} is not part of the allowed roles {DialogueRole.__as_list__()}.'
                  f' Defaulting to agent role ...')
            return DialogueRole._m_agent

        else:
            return role

    @classmethod
    def tool(cls):
        return cls(DialogueRole._m_tool)

    @classmethod
    def user(cls):
        return cls(DialogueRole._m_user)

    @classmethod
    def agent(cls):
        return cls(DialogueRole._m_agent)

    @classmethod
    def system(cls):
        return cls(DialogueRole._m_system)

    @classmethod
    def __as_list__(cls):
        as_list = []
        for name, value in cls.__dict__.items():
            if name.startswith("_m_"):
                as_list.append(value)
        return as_list
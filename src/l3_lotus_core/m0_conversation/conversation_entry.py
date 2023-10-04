from __future__ import annotations


class DialogueRole(str):
    _m_user = 'user'
    _m_agent = 'assistant'
    _m_system = 'system'
    _m_tool = 'function'

    def __new__(cls, role : str):
        if not role in DialogueRole.__as_list__():
            print(f'[Debug]: Given role {role} is not part of the allowed roles {DialogueRole.__as_list__()}.'
                  f' Defaulting to agent role ...')
            return str.__new__(cls, DialogueRole._m_agent)

        else:
            return str.__new__(cls, role)


    @classmethod
    def tool_role(cls):
        return cls(DialogueRole._m_tool)

    @classmethod
    def user_role(cls):
        return cls(DialogueRole._m_user)

    @classmethod
    def agent_role(cls):
        return cls(DialogueRole._m_agent)

    @classmethod
    def system_role(cls):
        return cls(DialogueRole._m_system)

    @classmethod
    def __as_list__(cls):
        as_list = []
        for name, value in cls.__dict__.items():
            if name.startswith("_m_"):
                as_list.append(value)
        return as_list


class Entry(dict):
    def __init__(self, role : DialogueRole, msg : str, tool_name ='undefined_function'):
        super().__init__()
        self['role'] = role
        self['content'] = msg
        if role == DialogueRole.tool_role():
            self['name'] = tool_name
        self._is_read : bool = False

    def __str__(self):
        return f'{self.get_role()}:{self.get_content()}\n'

    def get_is_enforce_mandate(self):
        return self.get_content().endswith('-m')

    def get_is_read(self) -> bool:
        return self._is_read

    def mark_read(self) -> None:
        self._is_read = True

    def get_role(self) -> str:
        return self['role']

    def get_content(self) -> str:
        return self['content']

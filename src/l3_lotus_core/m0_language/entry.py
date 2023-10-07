from __future__ import annotations
from typing import Optional

# ----------------------------------------------------

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


class Flag(str):
    _m_enforce_mandate  = 'm'

    def __new__(cls, flag : str):
        return str.__new__(cls, flag)

    @classmethod
    def enforce_mandate_flag(cls):
        return cls(flag=Flag._m_enforce_mandate)

    @classmethod
    def get_all_flagtypes(cls):
        as_list = []
        for name, value in cls.__dict__.items():
            if name.startswith("_m_"):
                as_list.append(value)
        return as_list


class Flags(list[Flag]):
    pass

class Entry(dict):
    def __init__(self, role : DialogueRole,
                 msg : str,
                 flags : Optional[Flags] = None,
                 tool_name = 'undefined_function'):
        super().__init__()
        self['role'] = role
        self['content'] = msg
        if role == DialogueRole.tool_role():
            self['name'] = tool_name
        self._is_processed : bool = False
        self.flags : Flags = flags if not flags is None else []

    def mark_processed(self):
        self._is_processed = True

    # ----------------------------------------------------

    def __str__(self):
        return f'{self.get_role()}:{self.get_content()}\n'

    def get_enforce_mandate_flag(self) -> bool:
        enforce_mandate : bool = False

        if Flag.enforce_mandate_flag() in self.flags:
            enforce_mandate = True

        print(f'[Temp Debug]: Enforcing mandate init: {enforce_mandate}')
        return enforce_mandate

    def get_is_read(self) -> bool:
        return self._is_processed

    def get_role(self) -> str:
        return self['role']

    def get_content(self) -> str:
        return self['content']

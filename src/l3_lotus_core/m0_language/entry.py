from __future__ import annotations
from typing import Optional
import inspect

# ----------------------------------------------------

class Entry(dict):
    def __init__(self, role : DialogueRole,
                 msg : str,
                 flags : Optional[list[Flag]] = None,
                 name : Optional[str] = 'None'):
        super().__init__()
        self['role'] = role
        self['content'] = msg

        if not name is None:
            self['name'] = name
        if role == DialogueRole.tool_role() and name is None:
            self['name'] = 'unnamed_function'
        self._is_processed : bool = False
        self.flags : list[Flag] = flags if not flags is None else []

    def mark_processed(self):
        self._is_processed = True

    # ----------------------------------------------------

    def __str__(self):
        return f'{self.get_role()}:{self.get_content()}\n'

    def append_content(self, additional_content : str):
        self['content'] += additional_content

    def get_name(self) -> Optional[str]:
        return self.get('name')

    def get_flags(self) -> list[Flag]:
        return self.flags

    def get_is_read(self) -> bool:
        return self._is_processed

    def get_role(self) -> DialogueRole:
        return self['role']

    def get_content(self) -> str:
        return self['content']



class DialogueRole(str):
    def __new__(cls, role_str : str):
        return str.__new__(cls, role_str)

    @classmethod
    def tool_role(cls):
        return cls(role_str='function')

    @classmethod
    def user_role(cls):
        return cls(role_str='user')

    @classmethod
    def agent_role(cls):
        return cls(role_str='assistant')

    @classmethod
    def system_role(cls):
        return cls(role_str='system')



class Flag(str):
    def __new__(cls, flag_str : str):
        return str.__new__(cls, flag_str)

    @classmethod
    def get_quit_flag(cls) -> Flag:
        return cls(flag_str='q')

    @classmethod
    def get_mandate_flag(cls) -> Flag:
        return cls(flag_str='m')

    @classmethod
    def get_reset_flag(cls) -> Flag:
        return cls(flag_str='r')

    @classmethod
    def get_all_flagtypes(cls):
        as_list = []
        for name, get_method in inspect.getmembers(cls, predicate=inspect.ismethod):
            if name.startswith('get') and name.endswith('flag'):
                flag = get_method()
                as_list.append(flag)
        return as_list



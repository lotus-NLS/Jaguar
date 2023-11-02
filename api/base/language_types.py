from __future__ import annotations

import inspect
from threading import Lock
from typing import Optional
from pydantic import BaseModel

# ----------------------------------------------

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
        self._is_processed : bool = True if not role == DialogueRole.user_role() else False
        self.flags : list[Flag] = flags if not flags is None else []

    def mark_processed(self):
        self._is_processed = True

    @classmethod
    def from_model(cls, entry_model) -> Entry:
        return cls(role=entry_model.role, msg=entry_model.content, flags=entry_model.flags)

    # ----------------------------------------------------

    def __str__(self):
        return f'{self.get_role()}:{self.get_content()}\n'

    def append_content(self, additional_content : str):
        self['content'] += additional_content

    def get_name(self) -> Optional[str]:
        return self.get('name')

    def get_flags(self) -> list[Flag]:
        return self.flags

    def get_is_processed(self) -> bool:
        return self._is_processed

    def get_role(self) -> DialogueRole:
        return self['role']

    def get_content(self) -> str:
        return self['content']


class EntryModel(BaseModel):
    role: str
    content: str
    flags: Optional[list[str]] = None

    def __init__(self, entry: Optional[Entry] = None, **data):
        if entry is not None:
            data['role'] = entry.get_role()
            data['content'] = entry.get_content()
            data['flags'] = entry.get_flags()
        super().__init__(**data)

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
    def try_from_str(cls, flag_str) -> Optional[Flag]:
        all_flags = cls.get_all_flagtypes()
        the_flag = None
        if flag_str in all_flags:
            the_flag = Flag(flag_str=flag_str)

        return the_flag

    @classmethod
    def get_entry_end_flag(cls) -> Flag:
        return cls(flag_str='e')

    @classmethod
    def get_print_threads_flag(cls) -> Flag:
        return cls(flag_str='t')

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


class SpeakerStaff:
    def __init__(self):
        self.lock = Lock()
        self.holder = None

    def acquire(self, holder):
        acquired = self.lock.acquire(blocking=False)  # Try to acquire the lock
        if acquired:
            self.holder = holder
        return acquired

    def release(self):
        self.lock.release()
        self.holder = None

    def current_holder(self):
        return self.holder

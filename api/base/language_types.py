from __future__ import annotations
from threading import Lock
from typing import Optional
from pydantic import BaseModel

# ----------------------------------------------

class Entry(dict):
    def __init__(self, role : DialogueRole,
                 msg : str,
                 flags : FlagContainer = None,
                 name : Optional[str] = 'None'):
        super().__init__()
        self['role'] = role
        self['content'] = msg

        if not name is None:
            self['name'] = name
        if role == DialogueRole.tool_role() and name is None:
            self['name'] = 'unnamed_function'
        self._is_processed : bool = True if not role == DialogueRole.user_role() else False
        self.flags : FlagContainer = flags if not flags is None else []

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

    def get_flags(self) -> FlagContainer:
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


class FlagContainer:
    def __init__(self, is_entry_end: bool = False, do_print_threads: bool = False, do_quit: bool = False, enforce_mandate: bool = False, do_reset: bool = False):
        self.is_entry_end: bool = is_entry_end
        self.print_threads: bool = do_print_threads
        self.quit: bool = do_quit
        self.mandate: bool = enforce_mandate
        self.reset: bool = do_reset

    @classmethod
    def make_default(cls):
        return cls()

    @classmethod
    def try_from_str(cls, flag_str: str) -> 'FlagContainer':
        this_container = cls()
        if '-e' in flag_str:
            this_container.is_entry_end = True
        if '-t' in flag_str:
            this_container.print_threads = True
        if '-q' in flag_str:
            this_container.quit = True
        if '-m' in flag_str:
            this_container.mandate = True
        if '-r' in flag_str:
            this_container.reset = True
        return this_container

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

import json
from typing import Optional
import ast
from .serializable import Serializable

# ----------------------------------------------

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


class FlagContainer(Serializable):
    def __init__(self, is_entry_end: bool = False,
                 do_print_threads: bool = False,
                 do_quit: bool = False,
                 enforce_mandate: bool = False,
                 do_reset: bool = False):
        self.is_entry_end: bool = is_entry_end
        self.print_threads: bool = do_print_threads
        self.quit: bool = do_quit
        self.mandate: bool = enforce_mandate
        self.reset: bool = do_reset


    @classmethod
    def make_default(cls):
        return cls()


    def as_text(self):
        flag_str = ""
        if self.is_entry_end:
            flag_str += '-e '
        if self.print_threads:
            flag_str += '-t '
        if self.quit:
            flag_str += '-q '
        if self.mandate:
            flag_str += '-m '
        if self.reset:
            flag_str += '-r '
        return flag_str.strip()

    @classmethod
    def from_text_specification(cls, flag_str: str):
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


class Entry(dict, Serializable):
    def __init__(self, role : DialogueRole,
                 msg : str,
                 flags : FlagContainer = None,
                 name : Optional[str] = 'None',
                 is_final : bool = False):
        super().__init__()
        self['role'] = role
        self['content'] = msg

        if role == DialogueRole.tool_role() and name is None:
            self['name'] = 'unnamed_function'
        else:
            self['name'] = name

        self._is_processed : bool = True if not role == DialogueRole.user_role() else False
        self.flags : FlagContainer = flags if not flags is None else FlagContainer.make_default()

        if is_final:
            self.flags.is_entry_end = True


    def mark_processed(self):
        self._is_processed = True

    # TODO: These methods strike me as unnecessarily verbose. They can surely be shortened
    def to_str(self) -> str:
        attr_dict = {
            'role': str(self['role']),
            'content': str(self['content']),
            'name': str(self.get('name')),
            'is_processed': str(self._is_processed),
            'flags': self.flags.to_str()
        }
        return json.dumps(attr_dict)

    @staticmethod
    def from_str(s: str):
        attr_dict = ast.literal_eval(s)
        role = attr_dict.get('role')
        content = attr_dict.get('content')
        name = attr_dict.get('name')
        is_processed = attr_dict.get('is_processed')
        flags_str = attr_dict.get('flags')

        new_entry = Entry(role=role, msg=content, flags=FlagContainer.from_str(s=flags_str), name=name)
        new_entry._is_processed = is_processed
        return new_entry


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





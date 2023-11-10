import json
from typing import Optional
import ast
from enum import Enum
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


class Flag(Enum):
    IS_ENTRY_START = '-s'
    IS_ENTRY_END = '-e'
    PRINT_THREADS = '-t'
    QUIT = '-q'
    MANDATE = '-m'
    RESET = '-r'


class FlagContainer(Serializable):
    def __init__(self):
        self.mapping : dict[str, bool] = {}


    def get(self, flag : Flag) -> bool:
        if not flag.value in self.mapping:
            return False
        else:
            return self.mapping[flag.value]


    def set(self, flag : Flag, value : bool):
        self.mapping[flag.value] = value


    @classmethod
    def make_default(cls):
        return cls()


class Entry(dict, Serializable):
    def __init__(self, role : DialogueRole,
                 msg : str,
                 flags : Optional[FlagContainer] = None,
                 name : Optional[str] = None,
                 is_final : bool = False):
        super().__init__()
        self['role'] = role
        self['content'] = msg

        if role == DialogueRole.tool_role() and name is None:
            self['name'] = 'unnamed_function'
        else:
            self['name'] = name if not name is None else role

        self._is_processed : bool = True if not role == DialogueRole.user_role() else False

        self.flags : FlagContainer = flags if not flags is None else FlagContainer.make_default()
        self.flags.set(flag=Flag.IS_ENTRY_END,value=is_final)


    def mark_processed(self):
        self._is_processed = True

    # TODO: These methods strike me as unnecessarily verbose. They can surely be shortened
    def serialize_as_str(self) -> str:
        attr_dict = {
            'role': str(self['role']),
            'content': str(self['content']),
            'name': str(self.get('name')),
            'is_processed': str(self._is_processed),
            'flags': self.flags.serialize_as_str()
        }
        return json.dumps(attr_dict)

    @staticmethod
    def from_serialized_str(s: str):
        attr_dict = ast.literal_eval(s)
        role = attr_dict.get('role')
        content = attr_dict.get('content')
        name = attr_dict.get('name')
        is_processed = attr_dict.get('is_processed')
        flags_str = attr_dict.get('flags')

        new_entry = Entry(role=role, msg=content, flags=FlagContainer.from_serialized_str(s=flags_str), name=name)
        new_entry._is_processed = is_processed
        return new_entry


    # ----------------------------------------------------

    def __str__(self):
        return f'{self.get_role()}:{self.get_content()}\n'

    def append_content(self, to_add : str):
        self['content'] += to_add

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





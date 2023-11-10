from typing import Optional
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


class Entry(Serializable):
    def __init__(self, role : DialogueRole,
                 msg : str, flags : Optional[FlagContainer] = None,
                 name : Optional[str] = None,
                 is_final : bool = False):

        backup_name = role if not role == DialogueRole.tool_role() else 'unnamed_function'
        name = name if not name is None else backup_name

        self.data : dict = {'role': role, 'content': msg, 'name' : name}
        self._is_processed : bool = True if not role == DialogueRole.user_role() else False
        self.flags : FlagContainer = flags if not flags is None else FlagContainer.make_default()
        self.flags.set(flag=Flag.IS_ENTRY_END, value=is_final)

    def as_dict(self):
        return self.data

    def mark_processed(self):
        self._is_processed = True

    def append_content(self, to_add : str):
        self.data['content'] += to_add

    # ----------------------------------------------------
    # get

    def get_content(self) -> str:
        return self.data['content']

    def get_role(self) -> DialogueRole:
        return self.data['role']

    def get_name(self) -> Optional[str]:
        return self.data['name']

    def get_flags(self) -> FlagContainer:
        return self.flags

    def get_is_processed(self) -> bool:
        return self._is_processed

    def __str__(self):
        return f'{self.get_role()}:{self.get_content()}\n'

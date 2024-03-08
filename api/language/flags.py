from enum import Enum


class Flag(Enum):
    IS_ENTRY_START = '-s'
    IS_ENTRY_END = '-e'
    PRINT_THREADS = '-t'
    QUIT = '-q'
    MANDATE = '-m'
    RESET = '-r'


class Flags(dict[str,bool]):
    def set(self, flag : Flag, value : bool):
        self[flag.value] = value

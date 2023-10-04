from typing import Optional
from src.l3_lotus_core import Flags,Flag


seperator = '|'

def get_parsed_input(the_input : str) -> (str, Optional[Flags]):
    if not seperator in the_input:
        msg, flags = the_input, None

    else:
        msg, flag_str = the_input.split(seperator)
        flags = Flags()
        for flag in Flag.get_all_flags():
            if flag in flag_str:
                flags.append(flag)

    return msg, flags


import time
from api.impl.client import LotusClient
from api.base.language_types import Entry, DialogueRole, Flag

# ----------------------------------------------

the_lotus_client = LotusClient()


time.sleep(0.5)
while True:
    user_input = input(f'Content?')
    flag_str = input(f'Flags?')

    flags = []
    for char in flag_str:
        flag = Flag.try_from_str(flag_str=char)
        if not flag is None:
            flags.append(flag)

    the_entry = Entry(msg=user_input,role= DialogueRole.agent_role(), flags=flags)
    the_lotus_client.send_user_entry(entry=the_entry)
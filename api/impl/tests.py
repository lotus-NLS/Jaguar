import time
from api.impl.client import LotusServer
from api.base.language_types import Entry, DialogueRole, FlagContainer

# ----------------------------------------------

the_lotus_client = LotusServer()


time.sleep(0.5)
while True:
    user_input = input(f'Content?')
    flag_str = input(f'Flags?')

    flags = FlagContainer.from_text_specification(flag_str=flag_str)
    the_entry = Entry(msg=user_input,role= DialogueRole.agent_role(), flags=flags)
    the_lotus_client.send_user_entry(entry=the_entry)
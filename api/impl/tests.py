import time
from api.impl.client import LotusClient
from api.base.language_types import Entry, DialogueRole

# ----------------------------------------------

the_lotus_client = LotusClient()


time.sleep(0.5)
while True:
    user_input = input()
    the_entry = Entry(msg=user_input,role= DialogueRole.agent_role())
    the_lotus_client.send_user_entry(entry=the_entry)
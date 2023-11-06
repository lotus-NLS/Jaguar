# import time
# from api.server.client import LotusClientIO
# from api.constants.language_types import Entry, DialogueRole, FlagContainer
# 
# # ----------------------------------------------
# 
# the_lotus_server = LotusClientIO(socketio=None)
# the_lotus_server.start()
# 
# time.sleep(0.5)
# while True:
#     user_input = input(f'Content?')
#     flag_str = input(f'Flags?')
# 
#     flags = FlagContainer.from_text_specification(flag_str=flag_str)
#     the_entry = Entry(msg=user_input,role= DialogueRole.agent_role(), flags=flags)
#     the_lotus_server.send_user_entry(entry=the_entry)
import time

import requests
from api.server.server import LotusServerIO


test_server = LotusServerIO()
test_server.start()


def test_create_item():
    url = "http://127.0.0.1:8000/item/"
    data = {"name": "Test Item", "description": "This is a test item."}
    response = requests.post(url, json=data)
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    time.sleep(1)
    test_create_item()
    while True:
        time.sleep(1)

import time
from api.impl.client import LotusClient


the_lotus_client = LotusClient()


time.sleep(0.5)
while True:
    user_input = input()
    the_lotus_client.send_user_msg(msg_content=f'{user_input}')
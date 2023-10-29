import time

from api.server import LotusServer
from api.impl.client import LotusClient


the_lotus_client = LotusClient()


time.sleep(0.5)

the_lotus_client.send_user_msg(msg_content='Hello ')


while True:
    time.sleep(5)
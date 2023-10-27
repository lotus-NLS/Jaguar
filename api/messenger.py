import requests
from requests import Response
from api.base_types import APIMessage
from api.server import LotusAPI_Server



class LotusAPI:

    def __init__(self, ip_addr : str, port : int):
        self.ip_add : str = ip_addr
        self.port : int = port

    def send_init(self, userID: str) -> Response:
        api_message_instance = APIMessage(user_id="some_user",msg_content='string')
        url = f"http://{self.ip_add}:{self.port}/{LotusAPI_Server.initialize.__name__}/"

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        the_dict = api_message_instance.model_dump()

        response = requests.get(url, headers=headers, json=the_dict)
        return response.json()



comm = LotusAPI(ip_addr='127.0.0.1',port=8000)
the_response = comm.send_init(userID='the_user')
print(the_response)
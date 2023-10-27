import requests
# from requests import Response
from api.base_types import APIMessage, ReqType, NetworkQuantities
from api.server import LotusServer

# ----------------------------------------------

class LotusAPI:
    def __init__(self, ip_addr : str = 'localhost', port : int = 8000):
        self.ip_add : str = ip_addr
        self.port : int = port

    def initialize_request(self, userID: str) -> str:
        response = self._communicate(endpoint=LotusServer.initialize.__name__,
                          req_type=ReqType.post(),
                          payload=APIMessage(user_id=f'{userID}'))

        return response


    def message_post_request(self,userID: str, msg_content : str) -> str:
        response = self._communicate(endpoint=LotusServer.get_message.__name__,
                                     req_type=ReqType.post(),
                                     payload=APIMessage(user_id=f'{userID}', msg_content=msg_content))
        return response


    def message_get_request(self, userID : str) -> str:
        response = self._communicate(endpoint=LotusServer.send_message.__name__,
                                     req_type=ReqType.get(),
                                     payload=APIMessage(user_id=f'{userID}'))

        return response



    def _communicate(self, endpoint : str, req_type : ReqType, payload : APIMessage) -> str:
        the_dict = payload.model_dump()
        url = f"http://{self.ip_add}:{self.port}/{endpoint}/"

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        req_function = requests.get if req_type == ReqType.get() else requests.post
        response = req_function(url, headers=headers, json=the_dict)
        return response.json()



comm = LotusAPI()
init_confirm = comm.initialize_request(userID='the_user')
receive_confirm = comm.message_post_request(userID='the_user', msg_content='bla bla')
server_message = comm.message_get_request(userID='the_user')

print(init_confirm)
print(receive_confirm)
print(server_message)
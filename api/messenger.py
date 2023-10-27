import requests
# from requests import Response
from api.base_types import APIMessage, ReqType
from api.server import LotusServer

# ----------------------------------------------

class LotusAPI:

    def __init__(self, ip_addr : str, port : int):
        self.ip_add : str = ip_addr
        self.port : int = port

    def initialize_request(self, userID: str) -> str:
        response = self._communicate(endpoint=LotusServer.initialize.__name__,
                          req_type=ReqType.post(),
                          payload=APIMessage(user_id=f'{userID}'))

        return response

    def message_get_request(self, userID : str) -> str:
        response = self._communicate(endpoint=LotusServer.get_message.__name__,
                                     req_type=ReqType.post(),
                                     payload=APIMessage(user_id=f'{userID}'))

        return response


    def message_post_request(self,userID: str, msg_content : str) -> str:
        response = self._communicate(endpoint=LotusServer.send_message.__name__,
                                     req_type=ReqType.get(),
                                     payload=APIMessage(user_id=f'{userID}', msg_content=msg_content))
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




comm = LotusAPI(ip_addr='127.0.0.1',port=8000)
sample_response = comm.initialize_request(userID='the_user')
# new_response = comm.message_post_request(userID='the_user',msg_content='bla bla')
print(sample_response)
# print(new_response)
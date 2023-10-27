import requests
# from requests import Response
from engine.l0_api.m1_api_types.base_types import APIMessage, ReqType
from engine.l0_api.m0_run.server import LotusAPI_Server

# ----------------------------------------------

class LotusAPI:

    def __init__(self, ip_addr : str, port : int):
        self.ip_add : str = ip_addr
        self.port : int = port

    def init_request(self, userID: str) -> dict:
        the_response = self.fetch_response(
                            endpoint=LotusAPI_Server.initialize.__name__,
                            req_type=ReqType.get(),
                            payload=APIMessage(user_id=f'{userID}'))

        return the_response

    def fetch_response(self, endpoint : str, req_type : ReqType, payload : APIMessage) -> dict:
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
sample_response = comm.init_request(userID='the_user')
print(sample_response)
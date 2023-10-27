import requests
from api.base_types import APIMessage, ReqType, NetworkQuantities
from api.server import LotusServer

# ----------------------------------------------

class LotusAPI:
    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = NetworkQuantities.default_port):
        self.ip_add : str = ip_addr
        self.port : int = port

    def init_request(self) -> str:
        response = self._communicate(endpoint=LotusServer.init_retriever.__name__,
                                     req_type=ReqType.post(),
                                     payload=APIMessage())

        return response


    def msg_post(self, msg_content : str) -> str:
        response = self._communicate(endpoint=LotusServer.msg_retriever.__name__,
                                     req_type=ReqType.post(),
                                     payload=APIMessage(msg_content=msg_content))
        return response


    def msg_get(self) -> str:
        response = self._communicate(endpoint=LotusServer.msg_sender.__name__,
                                     req_type=ReqType.get(),
                                     payload=APIMessage())

        return response

    # TODO:
    @staticmethod
    def get_confirmation() -> bool:
        return False

    def _communicate(self, endpoint : str, req_type : ReqType, payload : APIMessage) -> str:
        the_dict = payload.model_dump()
        url = f"http://{self.ip_add}:{self.port}/{endpoint}/"

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        req_function = requests.get if req_type == ReqType.get() else requests.post
        response = req_function(url, headers=headers, json=the_dict)

        try:
            the_response = response.json()
        except Exception as e:
            status_code = response.status_code
            reason = response.reason
            the_response =  f"Failed to decode JSON due to error:\"{e}\". Status Code: {status_code}, Reason: {reason}"

        return the_response



comm = LotusAPI()
# # init_confirm = comm.initialize_request(userID='the_user')
receive_confirm = comm.msg_post(msg_content='bla bla')
# server_message = comm.msg_get(userID='the_user')
#
# # print(init_confirm)
# print(receive_confirm)
# print(server_message)
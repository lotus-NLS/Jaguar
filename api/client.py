from api.io_module import IOModule
from api.base_types import APIMessage, ReqType, NetworkQuantities
from api.server import LotusServer

# ----------------------------------------------

class LotusClient(IOModule):
    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = NetworkQuantities.default_port):
        super().__init__(ip_addr=ip_addr,port=port)

    # TODO: This should actually be a get request made by the client not a post request made by the server
    def send_init_request(self) -> str:
        pass
        # response = self._communicate(endpoint=LotusServer.init_endpoint.__name__,
        #                              req_type=ReqType.get(),
        #                              payload=APIMessage())
        #
        # return response

    # TODO: This should actually be a get request made by the client not a post request made by the server
    def engine_message_endpoint(self, msg_content : str) -> str:
        pass
        # response = self._communicate(endpoint=LotusServer.outgoing_msg_handler.__name__,
        #                              req_type=ReqType.post(),
        #                              payload=APIMessage(msg_content=msg_content))
        # return response


    def send_user_msg(self) -> str:
        pass
        # response = self._communicate(endpoint=LotusServer.user_msg_endpoint.__name__,
        #                              req_type=ReqType.get(),
        #                              payload=APIMessage())
        #
        # return response

    def send_confirmation(self):
        pass
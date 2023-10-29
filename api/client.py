from api.io_module import LotusIO
from api.base_types import APIMessage, NetworkQuantities, ends

# ----------------------------------------------

class LotusClient(LotusIO):
    _instance = None
    _is_initialized = False

    def __new__(cls, *args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance
    
    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = NetworkQuantities.default_port):
        super().__init__(ip_addr=ip_addr,port=port)
        self.agent_data_endpoint = self.handle_endpoint(endpoint=ends.agent_data, handler=self.agent_data_handler)

    # ----------------------------------------------
    # Handlers

    def agent_data_handler(self, msg_content : str) -> str:
        response = self._communicate(endpoint=ends.agent_data, payload=APIMessage(msg_content=msg_content))
        return response

    # ----------------------------------------------
    # API

    def send_user_msg(self) -> None:
        self._communicate(endpoint=ends.user_data, payload=APIMessage())

    # TODO
    def send_confirmation(self):
        pass
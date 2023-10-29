from api.base.io_module import LotusIO
from api.base.api_types import APIMessage, NetworkQuantities, ends

# ----------------------------------------------

class LotusClient(LotusIO):
    _instance = None
    _is_initialized = False

    def __new__(cls, *args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance
    
    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = NetworkQuantities.default_client_port):
        super().__init__(ip_addr=ip_addr,port=port)
        self.agent_data_endpoint = self.handle_endpoint(endpoint=ends.agent_data, handler=self.agent_data_handler)
        self.start()

    # ----------------------------------------------
    # Handlers

    @staticmethod
    def agent_data_handler(lotus_msg : APIMessage) -> None:
        msg_content = lotus_msg.msg_content
        print(f'Client heard: {msg_content}')

    # ----------------------------------------------
    # API

    def send_user_msg(self,msg_content : str) -> None:
        self._communicate(endpoint=ends.user_data, payload=APIMessage(msg_content=msg_content))

    # TODO
    def send_confirmation(self):
        pass
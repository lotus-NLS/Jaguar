from pyutils import InputWaiter

from api.base.io_module import LotusIO
from api.base.api_types import APIMessage, NetworkQuantities, ends
# ----------------------------------------------

class LotusServer(LotusIO):
    _instance = None
    _is_initialized = False


    def __new__(cls, *args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance


    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = 8000):
        if not LotusServer._is_initialized:
            super().__init__(ip_addr=ip_addr,port=port)
            self.user_data_endpoint = self.handle_endpoint(endpoint=ends.user_data, handler=self._user_data_handler)
            self._incoming_msg_waiter : InputWaiter = InputWaiter()
            
            LotusServer._is_initialized = True

    # ----------------------------------------------
    # Handlers

    def _user_data_handler(self, lotus_msg: APIMessage) -> str:
        self._incoming_msg_waiter.write(lotus_msg.msg_content)
        return 'message ok'

    
    # ----------------------------------------------
    # API  

    def post_engine_message(self, msg_content : str) -> None:
        self._communicate(endpoint=ends.agent_data, payload=APIMessage(msg_content=msg_content))

    
    def get_user_msg(self) -> str:
        self._incoming_msg_waiter.clear()
        return self._incoming_msg_waiter.read()

    # TODO
    def get_confirmation(self) -> bool:
        pass

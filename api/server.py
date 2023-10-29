import uvicorn
import threading
from pyutils import InputWaiter

from api.io_module import IOModule
from api.base_types import ReqType, APIMessage, NetworkQuantities
# ----------------------------------------------

# TODO: The server make POST requests to the client instead of waiting for the client to retrieve the messages
class LotusServer(IOModule):
    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = 8000):
        super().__init__(ip_addr=ip_addr,port=port)
        self.user_messages = {}

        # Get requests to deploy
        self._make_endpoint(funct=self.init_endpoint, req_type=ReqType.post())
        self._make_endpoint(funct=self.user_msg_endpoint, req_type=ReqType.post())

        # Introduce message queue
        self.incoming_msg_waiter : InputWaiter = InputWaiter()
        self.init_waiter : InputWaiter = InputWaiter()

    # ----------------------------------------------

    def init_endpoint(self, lotus_msg: APIMessage) -> str:
        self.init_waiter.write(lotus_msg.user_id)
        return 'initialize ok'

    def get_init_signal(self) -> str:
        user_id = self.init_waiter.read()
        return user_id

    def user_msg_endpoint(self, lotus_msg: APIMessage) -> str:
        self.incoming_msg_waiter.write(lotus_msg.msg_content)
        return 'message ok'

    def get_user_msg(self) -> str:
        self.incoming_msg_waiter.clear()
        return self.incoming_msg_waiter.read()

    # ----------------------------------------------


    # TODO
    def post_engine_message(self, msg_content : str):
        pass

    # TODO
    def get_confirmation(self):
        pass


    # TODO
    def send_msg(self, msg : str):
        pass

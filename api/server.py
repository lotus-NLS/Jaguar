import uvicorn
import threading
from queue import Queue
from fastapi import FastAPI
from pyutils import InputWaiter

from api.base_types import ReqType, APIMessage, NetworkQuantities
# ----------------------------------------------

# TODO: The server make POST requests to the client instead of waiting for the client to retrieve the messages
class LotusServer:
    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = 8000):
        self.app = FastAPI()
        self.ip_add : str = ip_addr
        self.port : int = port
        self.user_messages = {}  # In-memory data structure to hold messages

        # Get requests to deploy
        self._make_endpoint(funct=self.incoming_init_handler, req_type=ReqType.get())
        self._make_endpoint(funct=self.incoming_msg_handler, req_type=ReqType.get())

        # Post requests to deploy
        self._make_endpoint(funct=self.outgoing_msg_handler, req_type=ReqType.post())

        # Introduce message queue
        self.incoming_msg_queue : Queue[str] = Queue()
        self.outgoing_msg_queue : Queue[str] = Queue()
        self.init_waiter : InputWaiter = InputWaiter()


    def start(self):
        def do_start():
            uvicorn_config = uvicorn.Config(app=self.app, host=self.ip_add, port=self.port)
            server = uvicorn.Server(config=uvicorn_config)
            server.run()

        threading.Thread(target=do_start).start()


    def _make_endpoint(self, funct : callable, req_type : ReqType):
        decorator = self.app.get if req_type == ReqType.get() else self.app.post
        decorator(f'/{funct.__name__}/')(funct)

    # TODO
    def post_engine_message(self, msg_content : str):
        pass

    # TODO
    def get_confirmation(self):
        pass


    # ----------------------------------------------

    def incoming_init_handler(self, lotus_msg: APIMessage) -> str:
        self.init_waiter.write(lotus_msg.user_id)
        return 'initialize ok'


    def incoming_msg_handler(self, lotus_msg: APIMessage) -> str:
        self.incoming_msg_queue.put(lotus_msg.msg_content)
        return 'message ok'


    def outgoing_msg_handler(self, lotus_msg: APIMessage) -> str:
        _ = lotus_msg
        try:
            the_msg = self.outgoing_msg_queue.get(timeout=0.5)
        except:
            the_msg = 'No messgae found for sending'
        return the_msg

    # ----------------------------------------------

    def get_init_signal(self) -> str:
        user_id = self.init_waiter.read()
        return user_id

    # TODO
    def get_user_msg(self) -> str:
        self.incoming_msg_queue = Queue()
        return self.incoming_msg_queue.get()

    def send_msg(self, msg : str):
        self.outgoing_msg_queue.put(msg)
        return


# def main():
#     # Create an instance of the class and get the FastAPI app object
#     my_server = LotusServer()
#     my_server.start()
#
#     print(my_server.get_msg())
#     print(my_server.get_init_signal())
#
#
# if __name__ == '__main__':
#     main()

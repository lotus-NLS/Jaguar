import threading
from queue import Queue
import uvicorn
from fastapi import FastAPI

from api.base_types import ReqType, APIMessage
# ----------------------------------------------

# TODO: IO should be based on user_id
class LotusServer:
    def __init__(self, ip_addr : str = 'localhost', port : int = 8000):
        self.app = FastAPI()
        self.ip_add : str = ip_addr
        self.port : int = port
        self.user_messages = {}  # In-memory data structure to hold messages

        # Get requests to deploy
        self._make_endpoint(funct=self.initialize, req_type=ReqType.post())
        self._make_endpoint(funct=self.get_message, req_type=ReqType.post())

        # Post requests to deploy
        self._make_endpoint(funct=self.send_message, req_type=ReqType.get())

        # Introduce message queue
        self.msg_queue : Queue[str] = Queue()


    def _make_endpoint(self, funct : callable, req_type : ReqType):
        decorator = self.app.get if req_type == ReqType.get() else self.app.post
        decorator(f'/{funct.__name__}/')(funct)

    # ----------------------------------------------

    @staticmethod
    def initialize(lotus_msg: APIMessage) -> str:
        return 'initialize ok'


    def get_message(self,lotus_msg: APIMessage) -> str:
        self.msg_queue.put(lotus_msg.msg_content)
        return 'message ok'


    @staticmethod
    def send_message(lotus_msg: APIMessage) -> str:
        return 'there is this message'
        # user_id = lotus_msg.user_id
        # content = lotus_msg.msg_content


    def get_msg(self):
        self.msg_queue = Queue()
        return self.msg_queue.get()

    # ----------------------------------------------

    def start(self):
        def do_start():
            uvicorn_config = uvicorn.Config(app=self.app, host=self.ip_add, port=self.port)
            server = uvicorn.Server(config=uvicorn_config)
            server.run()

        threading.Thread(target=do_start).start()


def main():
    # Create an instance of the class and get the FastAPI app object
    my_app = LotusServer()
    my_app.start()

    print(my_app.get_msg())


if __name__ == '__main__':
    main()

import uvicorn
from fastapi import FastAPI
from api.base_types import ReqType, APIMessage
# ----------------------------------------------

class LotusServer:
    def __init__(self, ip_addr : str, port : int):
        self.app = FastAPI()
        self.ip_add : str = ip_addr
        self.port : int = port
        self.user_messages = {}  # In-memory data structure to hold messages

        # Get requests to deploy
        self._make_endpoint(funct=self.initialize, req_type=ReqType.post())
        self._make_endpoint(funct=self.get_message, req_type=ReqType.post())

        # Post requests to deploy
        self._make_endpoint(funct=self.send_message, req_type=ReqType.get())

    def _make_endpoint(self, funct : callable, req_type : ReqType):
        decorator = self.app.get if req_type == ReqType.get() else self.app.post
        decorator(f'/{funct.__name__}/')(funct)

    # ----------------------------------------------

    @staticmethod
    def initialize(lotus_msg: APIMessage) -> str:
        return lotus_msg.model_dump_json()

    @staticmethod
    def get_message(lotus_msg: APIMessage) -> str:
        return lotus_msg.model_dump_json()

    @staticmethod
    def send_message(lotus_msg: APIMessage) -> str:
        pass
        # user_id = lotus_msg.user_id
        # content = lotus_msg.msg_content


    # ----------------------------------------------

    def run(self):
        uvicorn_config = uvicorn.Config(app=self.app, host=self.ip_add, port=self.port)
        server = uvicorn.Server(config=uvicorn_config)
        server.run()


def main():
    # Create an instance of the class and get the FastAPI app object
    my_app = LotusServer(ip_addr='127.0.0.1', port=8000)
    my_app.run()

if __name__ == '__main__':
    main()

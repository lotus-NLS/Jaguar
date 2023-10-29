import uvicorn
import requests
from fastapi import FastAPI
import threading
from api.base_types import ReqType, APIMessage, NetworkQuantities

# ----------------------------------------------

class IOModule:
    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = 8000):
        self.app = FastAPI()
        self.ip_addr : str = ip_addr
        self.port : int = port


    def start(self):
        def do_start():
            uvicorn_config = uvicorn.Config(app=self.app, host=self.ip_addr, port=self.port)
            server = uvicorn.Server(config=uvicorn_config)
            server.run()

        threading.Thread(target=do_start).start()


    def make_endpoint(self, funct : callable, req_type : ReqType):
        decorator = self.app.get if req_type == ReqType.get() else self.app.post
        decorator(f'/{funct.__name__}/')(funct)


    def _communicate(self, endpoint: str, req_type: ReqType, payload: APIMessage) -> str:
        the_dict = payload.model_dump()
        url = f"http://{self.ip_addr}:{self.port}/{endpoint}/"

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
            the_response = f"Failed to decode JSON due to error:\"{e}\". Status Code: {status_code}, Reason: {reason}"

        return the_response
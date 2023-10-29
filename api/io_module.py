import uvicorn
import requests
from fastapi import FastAPI
import threading
from api.base_types import ReqType, APIMessage, NetworkQuantities, Endpoint

# ----------------------------------------------

class LotusIO:
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


    def handle_endpoint(self,endpoint : Endpoint, handler : callable):
        decorator = self.app.get if endpoint.req_type == ReqType.get() else self.app.post
        decorator(f'/{endpoint.name}/')(handler)


    @staticmethod
    def _communicate(endpoint: Endpoint, payload: APIMessage) -> str:
        the_dict = payload.model_dump()
        url = f"http://{endpoint.ip_addr}:{endpoint.port}/{endpoint.name}/"

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        req_function = requests.get if endpoint.req_type == ReqType.get() else requests.post
        response = req_function(url, headers=headers, json=the_dict)

        try:
            the_response = response.json()
        except Exception as e:
            status_code = response.status_code
            reason = response.reason
            the_response = f"Failed to decode JSON due to error:\"{e}\". Status Code: {status_code}, Reason: {reason}"

        return the_response
import requests

from api import LotusRequest
from engine.l0_engine.server import Server


class DevUser:
    def __init__(self, engineIO : Server):
        self.engine_io : Server = engineIO
        self.buffer : str = ''

    def add_input(self, msg : str):
        self.buffer += msg

    def fire(self):
        req_str = LotusRequest(msg=self.buffer).model_dump_json()
        self.buffer = ''

        process_endpoint = self.engine_io.process_endpoint
        url = process_endpoint.get_url(protocol=self.engine_io.get_protocol())
        return requests.post(url=url, data=req_str, stream=True)



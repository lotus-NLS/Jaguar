from .endpoint import Endpoint, Socket, Method
from typing import Optional
from enum import Enum
import socket
import requests

class NetworkArea(Enum):
    LOCALHOST  = 'LOCALHOST'
    HOME = 'HOME'
    GLOBAL = 'WAN'


class Network:
    def __init__(self, webapp_socket : Optional[Socket] = None, engine_socket : Optional[Socket] = None):
        super().__init__()

        if not webapp_socket:
            webapp_socket = Socket(ip_addr=self.get_host(area=NetworkArea.LOCALHOST), port=5000)
        if not engine_socket:
            engine_socket = Socket(ip_addr=self.get_host(area=NetworkArea.LOCALHOST), port=5001)

        self.webapp_socket : Socket =  webapp_socket
        self.engine_socket : Socket =  engine_socket
        self.post_endpoint : Endpoint = Endpoint(name='post', method=Method.POST, socket=engine_socket)


    @classmethod
    def get_host(cls, area : NetworkArea) -> str:
        if area == NetworkArea.LOCALHOST:
            return '127.0.0.1'
        if area == NetworkArea.HOME:
            return cls.get_ip_addr(public=False)
        if area == NetworkArea.GLOBAL:
            raise PermissionError("Unable to retrieve Global IP automatically. Please check manually")


    @classmethod
    def get_ip_addr(cls, public : bool = True) -> str:
        if public:
            return cls._get_public_ip_addr()
        else:
            return socket.gethostbyname(socket.gethostname())


    @staticmethod
    def _get_public_ip_addr() -> str:
        err, public_ip = None, None
        try:
            response = requests.get('https://api.ipify.org')
            if response.status_code == 200:
                public_ip = response.text
            else:
                err = ConnectionError(f'Unable to retrieve public IP: {response.status_code}')
        except Exception as e:
            err = e
        if err:
            raise err
        return public_ip

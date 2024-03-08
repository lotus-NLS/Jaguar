import ipaddress
import socket as socket_lib
from enum import Enum


class Method(Enum):
    GET = 'GET'
    POST = 'POST'


class Socket:
    def __init__(self, ip: str, port: int):
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise ValueError("Invalid IP address")

        self.ip = ip
        self.port = port
        self.sock = socket_lib.socket(socket_lib.AF_INET, socket_lib.SOCK_STREAM)

    def as_addr(self):
        return f'{self.ip}:{self.port}'


class Endpoint:
    def __init__(self,socket : Socket, name : str, method : Method):
        self.location : str = name
        self.method : Method = method
        self.socket : Socket = socket

    def get_url(self) -> str:
        return f'//{self.socket.as_addr()}/{self.location}'

from flask import Flask
from PIL.Image import Image as PILImage
from abc import abstractmethod

from hollarek.templates import Singleton
from api import Network, Socket, Entry
from .types import ServerResponse, Task
from typing import Optional
# ----------------------------------------------

class Handler:
    @abstractmethod
    def handle(self, task : Task) -> ServerResponse:
        pass


class User:
    def __init__(self):
        self.io : EngineIO = EngineIO()

    @abstractmethod
    def send(self, msg : str, image : Optional[PILImage] = None) -> ServerResponse:
        pass


class EngineIO(Singleton):
    def __init__(self, handler : Optional[Handler] = None):
        if EngineIO.get_is_initialized():
            return

        super().__init__()
        if not handler:
            raise ValueError('Handler must be provided')
        self.entity : handler = handler
        self.app : Flask = Flask(__name__)

    def handle(self, task : Task) -> ServerResponse:
        return self.entity.handle(task=task)

    def run(self, socket : Socket = Network().engine_socket):
        self.app.run(port=socket.port, host=socket.ip)
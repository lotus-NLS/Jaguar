from flask import Flask
from PIL.Image import Image as PILImage
from abc import abstractmethod

from hollarek.logging import Loggable
from hollarek.templates import Singleton
from api import Network, Socket
from .types import Response, Task
from typing import Optional
# ----------------------------------------------

class Handler(Loggable):
    @abstractmethod
    def handle(self, task : Task) -> Response:
        pass


class User:
    def __init__(self):
        self.io : IO = IO()

    @abstractmethod
    def send(self, msg : str, image : Optional[PILImage] = None) -> Response:
        pass


class IO(Singleton):
    def __init__(self, handler : Optional[Handler] = None):
        if IO.get_is_initialized():
            return

        super().__init__()
        if not handler:
            raise ValueError('Handler must be provided')
        self.entity : handler = handler
        self.app : Flask = Flask(__name__)

    def handle(self, task : Task) -> Response:
        return self.entity.handle(task=task)

    def run(self, socket : Socket = Network().engine_socket):
        self.app.run(port=socket.port, host=socket.ip)


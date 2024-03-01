from flask import Flask
from abc import abstractmethod

from api import Entry, DefaultNetwork, Socket
from hollarek.tmpl import Singleton
from .types import ServerResponse, Task

# ----------------------------------------------

class Entity:
    @abstractmethod
    def handle(self, task : Task) -> ServerResponse:
        pass


class EngineIO(Singleton):
    def __init__(self, entity : Entity, app : Flask = Flask(__name__)):
        if EngineIO.is_initialized:
            return

        super().__init__()
        self.entity : entity = entity
        self.app : Flask = app

    def handle(self, task : Task) -> ServerResponse:
        return self.entity.handle(task=task)


    def run(self, socket : Socket = DefaultNetwork.engine_socket):
        self.app.run(port=socket.port, host=socket.ip)
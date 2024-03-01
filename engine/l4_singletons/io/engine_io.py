from flask import Flask
from abc import abstractmethod

from api import Entry, DefaultNetwork, Socket
from hollarek.tmpl import Singleton
from .types import ServerResponse

# ----------------------------------------------

class Entity:
    @abstractmethod
    def get_response(self, entry : Entry) -> ServerResponse:
        pass


class EngineIO(Singleton):
    def __init__(self, entity : Entity, app : Flask = Flask(__name__)):
        if EngineIO.is_initialized:
            return

        super().__init__()
        self.entity : entity = entity
        self.app : Flask = app

    def get_response_stream(self, entry : Entry) -> ServerResponse:
        return self.entity.get_response(entry=entry)


    def run(self, socket : Socket = DefaultNetwork.engine_socket):
        self.app.run(port=socket.port, host=socket.ip)
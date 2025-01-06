from __future__ import annotations

from engine.l0_engine.server.template import Server
from engine.l1_agents import Agent
from holytools.network import Socket


class ProductionServer(Server):
    def __init__(self, handler : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        super().__init__(handler=handler, socket=socket)

    @classmethod
    def get_protocol(cls) -> str:
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def kill(self):
        raise NotImplementedError

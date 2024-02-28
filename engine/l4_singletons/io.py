from typing import Optional
from flask import Flask
from api import DefaultNetwork, Entry
from hollarek.tmpl import Singleton

from engine.l4_singletons.io_types import TextStream, Server


# ----------------------------------------------


class EngineIO(Flask, Singleton):
    def __init__(self, server : Server, ip : Optional[str] = None, port : Optional[int] = None):
        if EngineIO.is_initialized:
            return

        Flask.__init__(self, import_name=__name__)
        Singleton.__init__(self)

        self.ip : str = ip if ip else DefaultNetwork.ip_engine
        self.port : int = port if port else DefaultNetwork.port_engine
        self.server : Server = server


    def get_response_stream(self, entry : Entry) -> TextStream:
        return self.server.get_response(entry=entry)

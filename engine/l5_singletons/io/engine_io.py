from flask import Flask, request, jsonify
from PIL.Image import Image as PILImage
from abc import abstractmethod
from typing import Optional

from hollarek.logging import Loggable
from hollarek.templates import Singleton
from api import Network, Socket
from api.communication.messages import Response, Task
from .transcribe import Transcriber
# ----------------------------------------------

class Handler(Loggable):
    @abstractmethod
    def handle(self, task : Task) -> Response:
        pass


class User:
    def __init__(self):
        self.io : IO = IO()
        self.transcriber : Transcriber = Transcriber()

    @abstractmethod
    def send(self, msg : str, image : Optional[PILImage] = None) -> Response:
        pass


class IO(Singleton):
    def __init__(self, handler : Optional[Handler] = None):
        if IO.get_is_initialized():
            return

        if not handler:
            raise ValueError('Handler must be provided')
        super().__init__()
        self.entity : handler = handler
        self.app : FastAPI = Flask(__name__)

        @app.post("/")
        async def process(request: Request):
            body_str = await request.body()  # Asynchronously get the request body
            task_str = body_str.decode('utf-8')  # Decode bytes to string
            return entity.handle(task=task_str)

        @app.post("/transcribe")
        async def transcribe(request: Request):
            body_str = await request.body()  # Asynchronously get the request body
            task_str = body_str.decode('utf-8')  # Decode bytes to string
            # Process the transcription based on the input task string
            return {"transcribed_text": "Dummy transcribed text based on " + task_str}


    def run(self, socket : Socket = Network().engine_socket):
        self.app.run(port=socket.port, host=socket.ip)


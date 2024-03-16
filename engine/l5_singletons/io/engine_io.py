from abc import abstractmethod
from typing import Optional
from fastapi import FastAPI
import uvicorn

from api import LotusRequest, TranscribeRequest, Socket, NetworkAddresses
from hollarek.logging import Loggable
from hollarek.templates import Singleton
from .types import Task
from .transcribe import Transcriber
# ----------------------------------------------


class Handler(Loggable):
    @abstractmethod
    def handle(self, task : Task) -> LotusRequest:
        pass


class IO(Singleton):
    def __init__(self, handler : Optional[Handler] = None):
        if IO.get_is_initialized():
            return

        if not handler:
            raise ValueError('Handler must be provided')
        super().__init__()
        self.entity : handler = handler
        self.transcriber : Transcriber = Transcriber()
        self.app : FastAPI = FastAPI()

        @self.app.post("/")
        async def process(request: LotusRequest):
            raise NotImplementedError
            # return self.entity.handle(task=request.messages)

        @self.app.post("/transcribe")
        async def transcribe(request: TranscribeRequest):
            raise NotImplementedError
            # body_str = await request.body()  # Asynchronously get the request body
            # task_str = body_str.decode('utf-8')  # Decode bytes to string
            # Process the transcription based on the input task string
            # return {"transcribed_text": "Dummy transcribed text based on " + task_str}


    def run(self, socket : Socket = NetworkAddresses().engine_socket):
        uvicorn.run(self.app, host=socket.ip, port=socket.port)


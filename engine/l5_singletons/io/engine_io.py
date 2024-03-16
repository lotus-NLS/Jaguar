import uvicorn
from abc import abstractmethod
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Optional

from api import LotusRequest, TranscribeRequest, Socket, Network, Entry
from hollarek.logging import Loggable
from hollarek.templates import Singleton
from .types import Task, Pipe
from .transcribe import Transcriber
# ----------------------------------------------


class Handler(Loggable):
    @abstractmethod
    def handle(self, task : Task) -> Pipe:
        pass


class IO(Singleton):
    def __init__(self, handler : Optional[Handler] = None):
        if IO.get_is_initialized():
            return

        if not handler:
            raise ValueError('Handler must be provided')
        super().__init__()
        self.handler : handler = handler
        self.transcriber : Transcriber = Transcriber()
        self.app : FastAPI = FastAPI()

        @self.app.post("/")
        async def process(request: LotusRequest) -> StreamingResponse:
            if request.img:
                raise NotImplementedError
            entry = [Entry.as_user(msg=request.msg)]
            task = Task(new_entries=entry)
            response = self.handler.handle(task=task)
            return StreamingResponse(content=response.get_text_stream(), media_type="text/plain")


        @self.app.post("/transcribe")
        async def transcribe(request: TranscribeRequest) -> str:
            raise NotImplementedError
            # body_str = await request.body()  # Asynchronously get the request body
            # task_str = body_str.decode('utf-8')  # Decode bytes to string
            # Process the transcription based on the input task string
            # return {"transcribed_text": "Dummy transcribed text based on " + task_str}


    def run(self, socket : Socket = Network().engine_socket):
        uvicorn.run(self.app, host=socket.ip, port=socket.port)


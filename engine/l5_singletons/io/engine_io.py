from __future__ import annotations

import uvicorn
from abc import abstractmethod
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Optional

from api import LotusRequest, TranscribeRequest, Socket, Network, Entry
from hollarek.logging import Loggable
from hollarek.templates import Singleton
from .pipes import TextPipe
from .transcribe import Transcriber
# ----------------------------------------------


class Handler(Loggable):
    @abstractmethod
    def handle(self, task : Task) -> TextPipe:
        pass


class IO(Singleton):
    def __init__(self, handler : Optional[Handler] = None, socket : Socket = Network().engine_socket):
        if IO.get_is_initialized():
            return

        if not handler:
            raise ValueError('Handler must be provided')
        super().__init__()
        self.handler : handler = handler
        self.transcriber : Transcriber = Transcriber()
        self.app : FastAPI = FastAPI()
        self.socket : Socket = socket

        @self.app.post("/")
        async def process(request: LotusRequest) -> str:
            if request.img:
                raise NotImplementedError
            entry = [Entry.as_user(msg=request.msg)]
            task = Task(new_entries=entry)
            response = self.handler.handle(task=task)
            return 'OK'
            # return StreamingResponse(content=response.get_text_stream(), media_type="text/plain")


        @self.app.post("/transcribe")
        async def transcribe(request: TranscribeRequest) -> str:
            return self.transcriber.get_text(wav_bytes=request.wav_bytes)

    def run(self):
        uvicorn.run(self.app, host=self.socket.ip, port=self.socket.port)


class Task:
    def __init__(self, new_entries : list[Entry] = None, required_tool_name : Optional[str] = None):
        self.new_entries : list[Entry] = new_entries if new_entries else []
        self.selected_tool : Optional[str] = required_tool_name
        self.skip_feedback : bool = False if self.selected_tool is None else True

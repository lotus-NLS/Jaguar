from __future__ import annotations

import inspect
import os.path
import time
import logging
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
        async def process(request: LotusRequest) -> SafeStream:
            if request.img:
                raise NotImplementedError
            entry = [Entry.as_user(msg=request.msg)]
            task = Task(new_entries=entry)
            response = self.handler.handle(task=task)

            def simple_text_stream():
                yield "Hello"
                time.sleep(1)
                raise ValueError(f'nope')
                yield " "
                time.sleep(1)
                yield "world!"
                time.sleep(1)
                yield "\nThis is a streaming response."
            return SafeStream(content=simple_text_stream(), media_type="text/plain")


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

import linecache

class SafeStream(StreamingResponse):
    logger = logging.getLogger(f'uvicorn.error')
    async def __call__(self, *args, **kwargs):
        try:
            return await super().__call__(*args, **kwargs)
        except BaseException as e:
            callstack = inspect.stack()
            while callstack:
                frame = callstack.pop()
                if os.path.abspath(__file__) in frame.filename:
                    file_path = frame.filename
                    line_number = frame.lineno
                    tb_str = (f'File "{file_path}", line {line_number}\n'
                              f'    {linecache.getline(file_path, line_number).strip()}')
                    print(f'{tb_str}')
            self.logger.error(f'Error during streaming: {e}')

from __future__ import annotations

import base64
import logging
import uvicorn
from multiprocessing import Process
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Optional

from api import LotusRequest, TranscribeRequest, Socket, Network, Entry
from hollarek.abstract import Singleton
from .task import Task, TaskHandler
from .transcribe import Transcriber

# ----------------------------------------------


class IO(Singleton):
    def __init__(self, handler : Optional[TaskHandler] = None, socket : Socket = Network().engine_socket):
        if IO.get_is_initialized():
            return

        if not handler:
            raise ValueError('Handler must be provided on initialization')
        super().__init__()
        self.handler : handler = handler
        self.transcriber : Transcriber = Transcriber()
        self.socket : Socket = socket

        self.app: FastAPI = FastAPI()
        self.dev_process: Optional[Process] = None

        @self.app.post("/")
        async def process(request: LotusRequest) -> SafeStream:
            if request.img:
                raise NotImplementedError
            entry = [Entry.as_user(msg=request.msg)]
            task = Task(new_entries=entry)

            response = self.handler.handle(task=task)
            return SafeStream(content=response.get_text_stream(), media_type="text/plain")


        @self.app.post("/transcribe")
        async def transcribe(request: TranscribeRequest) -> str:
            wav_bytes = base64.b64decode(request.wav_base64)
            return self.transcriber.get_text(wav_bytes=wav_bytes)


    def dev_run(self):
        def do():
            uvicorn.run(self.app, host=self.socket.ip, port=self.socket.port)
        self.dev_process = Process(target=do)
        self.dev_process.start()

    def dev_kill(self):
        self.dev_process.terminate()



class SafeStream(StreamingResponse):
    logger = logging.getLogger(f'uvicorn.error')
    async def __call__(self, *args, **kwargs):
        try:
            return await super().__call__(*args, **kwargs)
        except BaseException as e:
            endpoint = args[0].get('route')
            if not endpoint:
                f'Not found'
            self.logger.error(f'Error during streaming on endpoint \"{endpoint}\": {e}', exc_info=True)



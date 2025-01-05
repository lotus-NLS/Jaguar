from __future__ import annotations

import logging
from abc import abstractmethod
from multiprocessing import Process
from typing import Optional, Callable

import uvicorn
from fastapi.responses import StreamingResponse
from holytools.network import Socket, Endpoint, Method

from api import LotusRequest, Entry
from engine.l1_agents import Agent, Task


# ----------------------------------------------

class Server:
    def __init__(self, handler : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        super().__init__()
        self.handler : handler = handler
        # self.transcriber : Transcriber = Transcriber()
        self.socket : Socket = socket

        self.app: FastAPI = FastAPI()
        # self.add_endpoint(endpoint=self.get_transcribe_endpoint(), callback=self.transcribe)
        self.add_endpoint(endpoint=self.get_process_endpoint(), callback=self.respond)

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def kill(self):
        pass

    # ----------------------------------------------
    # callbacks

    async def respond(self, request: LotusRequest) -> SafeStream:
        if request.img:
            raise NotImplementedError
        entry = [Entry.as_user(msg=request.msg)]
        task = Task(new_entries=entry)

        response = self.handler.handle(task=task)
        return SafeStream(content=response.get_text_stream(), media_type="text/plain")

    # async def transcribe(self, request: TranscribeRequest) -> str:
    #     wav_bytes = base64.b64decode(request.wav_base64)
    #     return self.transcriber.get_text(wav_bytes=wav_bytes)

    # ----------------------------------------------

    def add_endpoint(self, endpoint : Endpoint, callback : Callable):
        if endpoint.method == Method.POST:
            decorator = self.app.post
        elif endpoint.method == Method.GET:
            decorator = self.app.get
        else:
            raise ValueError(f'Unsupported method: {endpoint.method}')
        decorator(endpoint.path)(callback)

    def get_transcribe_endpoint(self) -> Endpoint:
        return Endpoint(path='/transcribe', method=Method.POST, socket=self.socket)

    def get_process_endpoint(self) -> Endpoint:
        return Endpoint(path='/process', method=Method.POST, socket=self.socket)

    @classmethod
    @abstractmethod
    def get_protocol(cls) -> str:
        pass

import html
from fastapi import FastAPI, Response
from engine.l2_models import Context

class DevServer(Server):
    def __init__(self, handler : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        super().__init__(handler=handler, socket=socket)
        self.handler : handler = handler
        self.dev_process: Optional[Process] = None
        self.add_endpoint(endpoint=self.get_context_endpoint(), callback=self.get_context_view)

    def get_context_endpoint(self, *args, **kwargs) -> Endpoint:
        _, __ = args, kwargs
        return Endpoint(path='/context', method=Method.GET, socket=self.socket)

    def get_context_view(self) -> Response:

        system_context =  Context(entries=[self.handler.get_system_prompt()])
        os_context = self.handler.os.get_context()
        memory = Context(entries=self.handler.memory)
        context_str = system_context.as_str(section_header=f'System prompt')
        context_str += os_context.as_str(section_header=f'Lotus Operating System')
        context_str += memory.as_str(section_header=f'Memory')

        escaped_context = html.escape(context_str)
        html_context = escaped_context.replace("\n", "<br>")
        html_context = f'<pre> {html_context} </pre>'
        return Response(content=html_context, media_type="text/html")

    def run(self):
        def do():
            uvicorn.run(self.app, host=self.socket.ip, port=self.socket.port)
        self.dev_process = Process(target=do)
        self.dev_process.start()

    def kill(self):
        self.dev_process.terminate()

    @classmethod
    def get_protocol(cls):
        return 'http'


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



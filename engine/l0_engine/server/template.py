from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Callable

from fastapi.responses import StreamingResponse
from holytools.network import Socket, Endpoint, Method

from api import LotusRequest, Entry
from engine.l1_agents import Agent, Task
from fastapi import FastAPI


# ----------------------------------------------

class Server:
    def __init__(self, handler : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        super().__init__()
        self.handler : handler = handler
        self.socket : Socket = socket
        self.app: FastAPI = FastAPI()

        self.process_endpoint = Endpoint(path='/process', method=Method.POST, socket=self.socket)
        self.add_action(endpoint=self.process_endpoint, callback=self.respond)


    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def kill(self):
        pass

    @classmethod
    @abstractmethod
    def get_protocol(cls) -> str:
        pass

    def add_action(self, endpoint : Endpoint, callback : Callable):
        if endpoint.method == Method.POST:
            decorator = self.app.post
        elif endpoint.method == Method.GET:
            decorator = self.app.get
        else:
            raise ValueError(f'Unsupported method: {endpoint.method}')
        decorator(endpoint.path)(callback)

    # --------------------------------------------

    async def respond(self, request: LotusRequest) -> SafeStream:
        if request.img:
            raise NotImplementedError
        entry = [Entry.as_user(msg=request.msg)]
        task = Task(new_entries=entry)

        response = self.handler.handle(task=task)
        return SafeStream(content=response.get_text_stream(), media_type="text/plain")


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



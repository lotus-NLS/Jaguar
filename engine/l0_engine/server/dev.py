from __future__ import annotations

import html
from multiprocessing import Process
from typing import Optional

import uvicorn
from starlette.responses import Response

from engine.l0_engine.server.template import Server
from engine.l1_agents import Agent
from engine.l2_models import Context
from holytools.network import Socket, Endpoint, Method


class DevServer(Server):
    def __init__(self, handler : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        super().__init__(handler=handler, socket=socket)
        self.handler : handler = handler
        self.dev_process: Optional[Process] = None
        context_endpoint = Endpoint(path='/context', method=Method.GET, socket=self.socket)
        self.add_action(endpoint=context_endpoint, callback=self.get_context_view)

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

    # ----------------------------------
    # callbacks

    def get_context_view(self) -> Response:
        system_context =  Context(entries=[self.handler._get_system_prompt()])
        os_context = Context.from_aos(aos=self.handler.aos)
        memory = Context(entries=self.handler.memory)
        context_str = system_context.as_str(section_header=f'System prompt')
        context_str += os_context.as_str(section_header=f'Lotus Operating System')
        context_str += memory.as_str(section_header=f'Memory')

        escaped_context = html.escape(context_str)
        html_context = escaped_context.replace("\n", "<br>")
        html_context = f'<pre> {html_context} </pre>'
        return Response(content=html_context, media_type="text/html")

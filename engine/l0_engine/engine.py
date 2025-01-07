import time

import html
import os
import sys
from multiprocessing import Process
from typing import Optional
import uvicorn
from starlette.responses import Response

from holytools.logging import Loggable
from holytools.network import Socket, Endpoint, Method

from engine.l3_aos import AOS, TextEditor, Terminal, FileExplorer, Browser
from engine.l2_models import OpenAIModel
from engine.l2_models import Context
from engine.l1_agents import Agent
from engine.l0_engine.server.template import Server

from .settings import LotusCredentials
from .users.developer import DevUser

# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self, use_local_credentials : bool = True):
        super().__init__()
        creds = LotusCredentials(use_local=use_local_credentials)

        model = OpenAIModel.default_model(api_key=creds.get_openai_apikey())
        browser = Browser(google_api_key=creds.get_google_apikey(), searchengine_id=creds.get_searchengine_id())
        aos: AOS = AOS(workspaces=[TextEditor(), Terminal(), FileExplorer(), browser])
        self.handler: Agent = Agent(model=model, aos=aos)
        self.engine_io: Server = DevServer(handler=self.handler)

    def launch(self, on_console : bool):
        self.log(f'Lotus started')
        self.engine_io.run()
        if on_console:
            self._launch_console()
        else:
            raise NotImplementedError('Webapp not yet implemented')
        self.stop()

    def _launch_console(self):
        dev_user = DevUser(engineIO=self.engine_io)
        while True:
            user_input = input(f'\nUser: ')
            if user_input == 'exit':
                break
            dev_user.add_input(msg=user_input)
            response = dev_user.make_request()
            print(f'GOTO: ', end='')
            for text in response.iter_content(chunk_size=None, decode_unicode=True):
                print(text, end='', flush=True)
                time.sleep(0.05)

    def stop(self):
        self.log(f'Lotus stopped')
        self.engine_io.kill()


class DevServer(Server):
    def __init__(self, handler : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        super().__init__(handler=handler, socket=socket)
        self.handler : handler = handler
        self.dev_process: Optional[Process] = None
        context_endpoint = Endpoint(path='/context', method=Method.GET, socket=self.socket)
        self.add_action(endpoint=context_endpoint, callback=self.get_context_view)

    def run(self):
        def do():
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
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
        system_context =  Context(entries=[self.handler.get_system_prompt()])
        os_context = Context.from_aos(aos=self.handler.aos)
        memory = Context(entries=self.handler.memory)

        context_str = system_context.as_str(section_header=f'System prompt')
        context_str += os_context.as_str(section_header=f'Lotus Operating System')
        context_str += memory.as_str(section_header=f'Memory')

        escaped_context = html.escape(context_str)
        html_context = escaped_context.replace("\n", "<br>")
        html_context = f'<pre> {html_context} </pre>'
        return Response(content=html_context, media_type="text/html")
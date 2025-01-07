import html
import os
import sys
import time
from multiprocessing import Process
from typing import Optional, Callable

import uvicorn
from fastapi import FastAPI
from starlette.responses import Response

from api import Entry
from engine.l1_agents import Agent, Task
from engine.l2_models import Context
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, TextEditor, Terminal, FileExplorer, Browser
from holytools.logging import Loggable
from holytools.network import Socket, Method
from .settings import LotusCredentials


# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self, use_local_credentials : bool = True):
        super().__init__()
        self.creds = LotusCredentials(use_local=use_local_credentials)
        self.agent: Agent = Agent(model=self.get_model(), aos=self.get_aos())
        self.dev_monitor : MonitorServer = MonitorServer(agent=self.agent)

    def get_model(self):
        return OpenAIModel.default_model(api_key=self.creds.get_openai_apikey())

    def get_aos(self):
        browser = Browser(google_api_key=self.creds.get_google_apikey(), searchengine_id=self.creds.get_searchengine_id())
        return AOS(workspaces=[TextEditor(), Terminal(), FileExplorer(), browser])

    def launch(self):
        self.log(f'Lotus started')
        while True:
            user_input = input(f'\nUser: ')
            if user_input == 'exit':
                break
            print(f'GOTO: ', end='')
            task = Task(new_entries=[Entry.user(msg=user_input)])
            response = self.agent.handle(task=task)
            for text in response.get_text_stream():
                print(text, end='', flush=True)
                time.sleep(0.05)

        self.stop()

    def stop(self):
        self.log(f'Lotus stopped')
        self.dev_monitor.kill()


class MonitorServer:
    def __init__(self, agent : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        super().__init__(socket=socket)
        self.agent : Agent = agent
        self.socket : Socket = socket
        self.app: FastAPI = FastAPI()
        self.process: Optional[Process] = None

        self.add_action(relpath=f'/context', method=Method.GET, callback=self.get_context_view)

    def add_action(self, relpath : str, method : Method, callback : Callable):
        if method == Method.POST:
            decorator = self.app.post
        elif method == Method.GET:
            decorator = self.app.get
        else:
            raise ValueError(f'Unsupported method: {method}')
        decorator(f'{self.get_protocol()}://{self.socket}{relpath}')(callback)

    def run(self):
        def do():
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            uvicorn.run(self.app, host=self.socket.ip, port=self.socket.port)
        self.process = Process(target=do)
        self.process.start()

    def kill(self):
        self.process.terminate()

    @classmethod
    def get_protocol(cls) -> str:
        return 'http'

    # ----------------------------------
    # callbacks

    def get_context_view(self) -> Response:
        system_context =  Context(entries=[self.agent.get_system_prompt()])
        os_context = Context.from_aos(aos=self.agent.aos)
        memory = Context(entries=self.agent.memory)

        context_str = system_context.as_str(section_header=f'System prompt')
        context_str += os_context.as_str(section_header=f'Lotus Operating System')
        context_str += memory.as_str(section_header=f'Memory')

        escaped_context = html.escape(context_str)
        html_context = escaped_context.replace("\n", "<br>")
        html_context = f'<pre> {html_context} </pre>'
        return Response(content=html_context, media_type="text/html")
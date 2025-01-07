import html
import logging
import threading
import time
from typing import Optional

from flask import Flask

from api import Entry
from engine.l1_agents import Agent, Task
from engine.l2_models import Context
from engine.l2_models import OpenAIModel
from engine.l3_aos import AOS, TextEditor, Terminal, FileExplorer, Browser
from holytools.logging import Loggable
from holytools.network import Socket
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

    # ---------------------------------------------

    def conversation_routine(self):
        self.launch()
        while True:
            user_input = input(f'\nUser: ')
            if user_input == 'exit':
                break

            task = Task(new_entries=[Entry.user(msg=user_input)])
            response = self.agent.handle(task=task)
            for text in response.get_text_stream():
                print(text, end='', flush=True)
                time.sleep(0.05)

            time.sleep(0.5)


    def request_terminal(self):
        self.launch()
        task = Task(new_entries=[Entry.user(msg='Open terminal in /home/daniel')])
        response = self.agent.handle(task=task)
        for text in response.get_text_stream():
            print(text)

    def launch(self):
        self.log(f'Lotus started')
        self.dev_monitor.run()
        time.sleep(1)

    def stop(self):
        self.log(f'Lotus stopped')
        self.dev_monitor.kill()


class MonitorServer:
    def __init__(self, agent : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        self.agent : Agent = agent
        self.socket : Socket = socket
        self.app: Flask = Flask(__name__)
        self.thread: Optional[threading.Thread] = None

        @self.app.route(f'/context')
        def get_context_view() -> str:
            system_context = Context(entries=[self.agent.get_system_prompt()])
            os_context = Context.from_aos(aos=self.agent.aos)
            memory = Context(entries=self.agent.memory)

            context_str = system_context.as_str(section_header=f'System prompt')
            context_str += os_context.as_str(section_header=f'Lotus Operating System')
            context_str += memory.as_str(section_header=f'Memory')

            escaped_context = html.escape(context_str)
            html_context = escaped_context.replace("\n", "<br>")
            html_context = f'<pre> {html_context} </pre>'
            return html_context


    def run(self):
        def do():
            logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
            self.app.run(host=self.socket.ip, port=self.socket.port)
        self.thread = threading.Thread(target=do)
        self.thread.start()

    def kill(self):
        self.thread._stop()


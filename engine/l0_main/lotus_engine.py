import threading
import time
import uuid
from queue import Queue
from typing import Optional

from flask import Flask
from flask_socketio import SocketIO, emit

from engine.l0_main.dev_monitor import DevMonitor
from engine.l1_agents import Agent, Evaluator, Task, TaskTracker
from engine.l2_models import OpenAIModel, State, InfConfig
from engine.l3_aos import AOS, Terminal, Browser
from holytools.abstract import Serializable
from holytools.logging import Loggable
from engine.l0_main.settings import LotusCredentials
from engine.l1_agents.guidance.workflow import Workflow, Node
from engine.l2_models.generation.step import Report, Step
from engine.l2_models.language import Message
from engine.l2_models.llm import LLM
from engine.l3_aos.workspaces.python_ide import PythonIDE
from holytools.network import Endpoint


# ---------------------------------------------------------

class LotusEngine(Loggable):
    def __init__(self):
        super().__init__()
        self._creds: LotusCredentials = LotusCredentials.from_file()
        self.sess_uuid: str = self.generate_session_uuid()

        model = OpenAIModel.default_model(api_key=self._creds.openai_api_key)
        self.agent = self.make_agent(model=model)
        self._evalutor : Evaluator = Evaluator(model=model)

        dev_monitor : DevMonitor = DevMonitor.default()
        self.step_endpoint: Endpoint = dev_monitor.step_endpoint
        self.outgoing_messages : Queue[Message] = Queue()
        self.start_socket()

    @staticmethod
    def generate_session_uuid() -> str:
        return str(uuid.uuid4()) + str(uuid.uuid4())

    def make_agent(self, model : LLM) -> Agent:
        creds  = self._creds
        browser = Browser(google_api_key=creds.google_api_key, searchengine_id=creds.search_engine_id)
        terminal = Terminal()
        ide = PythonIDE()
        aos = AOS(workspaces=[terminal, browser, ide])


        return Agent(aos=aos, model=model)

    def start_socket(self):
        app = Flask(__name__)
        socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

        @app.route('/')
        def index():
            return "Hello, this is the main page!"

        @socketio.on('connect')
        def handle_connect():
            emit('uuid', {'uuid': self.generate_session_uuid()})

        def start():
            socketio.run(app, host='localhost', port=8000, allow_unsafe_werkzeug=True)

        def send_outgoing():
            while True:
                msg = self.outgoing_messages.get()
                print(f'Emitting message to socket: {msg.text}')
                socketio.emit('msg', {'role': msg.role.value, 'content': msg.text})

        socketio.start_background_task(start)
        socketio.start_background_task(send_outgoing)

    # ---------------------------------------------------------------------------------------
    # routines

    def testroutine(self):
        while True:
            time.sleep(2)
            msg = Message.user(msg='Hello world')
            self.outgoing_messages.put(msg)

    def do_workflow(self, wf : Workflow) -> Node:
        node = wf.start_node
        outgoing_edges = wf.outgoing_edge_map[node.name]

        workflow_description = Message.system(msg=wf.notice)
        self.agent.update_memory(entry=workflow_description)

        while True:
            print(f'## Now starting work on node: {node.name}')
            self.do_task(task=node.task, max_steps=node.max_steps)

            if not node.name in wf.outgoing_edge_map:
                break

            exit_tool = wf.get_exit_tool(node_name=node.name)
            self.agent.update_memory(entry=Message.tool(msg=exit_tool.get_desc(), name=exit_tool.get_name()))
            self.agent.handle(inf_config=InfConfig(required_tool=exit_tool))
            choice = exit_tool.exit_choice.get_value()
            node = outgoing_edges[choice].target

        return node

    def do_task(self, task : Task, max_steps : int, dos : Optional[str] = None):
        writings : list[str] = []
        for step in self.agent.work(task=task, max_steps=max_steps):
            print()
            w = self.observe(step=step)
            writings.append(w)
        print(f'Finished work mode after {len(writings)} steps')

        if not dos is None:
            report = writings[-1]
            if not report:
                raise ValueError('No summary generated')

            is_successful = self._evalutor.evaluateProperty(report=report, prop=dos)
            report = Report(summary=report, is_successful=is_successful, sess_uuid=self.sess_uuid)

    def converse(self):
        while True:
            print('User: ', end='')
            user_input = input()
            if user_input == 'exit':
                break

            user_mesage = Message.user(msg=user_input)
            self.outgoing_messages.put(user_mesage)

            step = self.agent.talk(msg=user_input)
            self.observe(step=step)

            print()

    def observe(self, step : Step) -> str:
        text = ''
        for chunk in step.text_pipe.get_text_stream():
            text += chunk
            print(chunk, end='')
        self.send(endpoint=self.step_endpoint, obj=step.get_state(uuid=self.sess_uuid))

        for o in step.tool_outputs:
            if not TaskTracker.get_name() in o.tool_name:
                msg = Message.from_tool_output(tool_output=o)
                self.outgoing_messages.put(msg)

        if text:
            msg = Message.agent(msg=text)
            self.outgoing_messages.put(msg)

        return text

    def send(self, endpoint : Endpoint, obj : Serializable):
        try:
            endpoint.post(msg=obj.to_str(), secure=False)
        except:
            self.warning(f'Monitor endpoint {endpoint.get_url(protocol=f"https")} unresponsive')

if __name__ == "__main__":
    engine = LotusEngine()
    engine.testroutine()
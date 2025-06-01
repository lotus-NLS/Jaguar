import sys
import time
import uuid
from queue import Queue

from flask import Flask
from flask_socketio import SocketIO, emit

from engine.l0_main.settings import DefaultPorts
from engine.l0_main.dev_monitor import ContextMonitor
from engine.l1_agents.tasks.tasktracker import TaskTracker
from engine.l2_models.generation.step import Step, TextPipe
from engine.l2_models.language import Message
from holytools.abstract import Serializable
from holytools.logging import LoggerFactory
from holytools.logging.timber import Timber
from holytools.network import Endpoint

# ---------------------------------------------------------

class LotusIO(Timber):
    def __init__(self, disable_socket : bool = False, io_port : int = DefaultPorts.socket_port):
        super().__init__()
        self.sess_uuid: str = self.generate_session_uuid()
        self.io_port : int = io_port

        dev_monitor : ContextMonitor = ContextMonitor.default()
        self.step_endpoint: Endpoint = dev_monitor.step_endpoint
        self.outgoing_messages : Queue[Message] = Queue()
        if not disable_socket:
            self.start_socket()

    def send(self, message : Message):
        self.outgoing_messages.put(message)

    @staticmethod
    def generate_session_uuid() -> str:
        return str(uuid.uuid4()) + str(uuid.uuid4())

    def start_socket(self):
        # TODO: This is temporarily disabled until this logging becomes relevant
        # TODO: In the meantime don't forget "WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead."
        werkzeug_logger = LoggerFactory.get_logger(name='werkzeug')
        werkzeug_logger.disabled = True

        app = Flask(__name__)
        socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

        @app.route('/')
        def index():
            return "Hello, this is the main page!"

        @socketio.on('connect')
        def handle_connect():
            emit('uuid', {'uuid': self.generate_session_uuid()})

        def start():
            socketio.run(app, host='localhost', port=self.io_port, allow_unsafe_werkzeug=True)

        def send_outgoing():
            while True:
                msg = self.outgoing_messages.get()
                socketio.emit('msg', {'role': msg.role.value, 'content': msg.text})

        socketio.start_background_task(start)
        socketio.start_background_task(send_outgoing)

    def observe(self, step : Step) -> str:
        if step.is_failed():
            self.error(f'Failed step: {step.err_msg}')
            return ''


        self.post(endpoint=self.step_endpoint, obj=step.get_state(uuid=self.sess_uuid))
        if step.text_pipe:
            text = self.observe_pipe(text_pipe=step.text_pipe)
        else:
            text = ''

        for o in step.tool_outputs:
            if not TaskTracker.get_name() in o.tool_name:
                msg = Message.from_tool_output(tool_output=o)
                self.outgoing_messages.put(msg)
            for update in o.prog_updates:
                self.info(str(update))

        if text:
            msg = Message.agent(text=text)
            self.outgoing_messages.put(msg)

        return text

    @staticmethod
    def observe_pipe(text_pipe : TextPipe) -> str:
        text = ''
        stream = text_pipe.get_text_stream()
        try:
            first_chunk = stream.__next__()
            if first_chunk:
                print(f'Assistant {first_chunk}', end='')
                text += first_chunk
            for chunk in text_pipe.get_text_stream():
                time.sleep(0.05)
                text += chunk
                print(chunk, end='')
                sys.stdout.flush()
            print('\n')
        except StopIteration:
            pass

        return text

    def post(self, endpoint : Endpoint, obj : Serializable):
        try:
            self.info(f'Making post request to {endpoint.get_url(protocol="https")}')
            endpoint.post(msg=obj.to_str(), secure=False)
        except:
            self.warning(f'Monitor endpoint {endpoint.get_url(protocol=f"https")} unresponsive')



if __name__ == "__main__":
    io = LotusIO()
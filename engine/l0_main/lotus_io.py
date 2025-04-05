import sys
import tempfile
import time
import uuid
from queue import Queue

from flask import Flask
from flask_socketio import SocketIO, emit

from engine.l0_main.dev_monitor import DevMonitor
from engine.l1_agents import TaskTracker
from engine.l2_models.generation.step import Step
from engine.l2_models.language import Message
from holytools.abstract import Serializable
from holytools.logging import Loggable
from holytools.network import Endpoint

temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+t')
print(f'Temp file created: {temp_file.name}')

# ---------------------------------------------------------

class LotusIO(Loggable):
    def __init__(self):
        super().__init__()
        self.sess_uuid: str = self.generate_session_uuid()

        dev_monitor : DevMonitor = DevMonitor.default()
        self.step_endpoint: Endpoint = dev_monitor.step_endpoint
        self.outgoing_messages : Queue[Message] = Queue()
        self.start_socket()

    def send(self, message : Message):
        self.outgoing_messages.put(message)

    @staticmethod
    def generate_session_uuid() -> str:
        return str(uuid.uuid4()) + str(uuid.uuid4())

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
            sys.stdout = temp_file
            sys.stderr = temp_file
            socketio.run(app, host='localhost', port=8000, allow_unsafe_werkzeug=True)

        def send_outgoing():
            sys.stdout = temp_file
            sys.stderr = temp_file

            while True:
                msg = self.outgoing_messages.get()
                print(f'Emitting message to socket: {msg.text}')
                socketio.emit('msg', {'role': msg.role.value, 'content': msg.text})

        socketio.start_background_task(start)
        socketio.start_background_task(send_outgoing)

    def observe(self, step : Step) -> str:
        text = ''
        print('Assistant: ', end='')
        for chunk in step.text_pipe.get_text_stream():
            time.sleep(0.05)
            text += chunk
            print(chunk, end='')
        print()
        self.post(endpoint=self.step_endpoint, obj=step.get_state(uuid=self.sess_uuid))

        for o in step.tool_outputs:
            if not TaskTracker.get_name() in o.tool_name:
                msg = Message.from_tool_output(tool_output=o)
                self.outgoing_messages.put(msg)

        if text:
            msg = Message.agent(msg=text)
            self.outgoing_messages.put(msg)

        return text

    def post(self, endpoint : Endpoint, obj : Serializable):
        try:
            endpoint.post(msg=obj.to_str(), secure=False)
        except:
            self.warning(f'Monitor endpoint {endpoint.get_url(protocol=f"https")} unresponsive')

if __name__ == "__main__":
    lotus_io = LotusIO()
import html
import logging
import threading
from typing import Optional

from flask import Flask

from engine.l1_agents import Agent
from holytools.network import Socket


class MonitorServer:
    def __init__(self, agent : Agent, socket : Socket = Socket.get_localhost(port=5000)):
        self.agent : Agent = agent
        self.socket : Socket = socket
        self.app: Flask = Flask(__name__)
        self.thread: Optional[threading.Thread] = None

        @self.app.route(f'/context')
        def get_context_view() -> str:
            context = agent.get_context()
            context_str = context.as_str(section_header=f'Agent context')
            escaped_context = html.escape(context_str)
            html_context = escaped_context.replace("\n", "<br>")
            html_context = f'<pre> {html_context} </pre>'
            return html_context

    def serve(self):
        def do():
            logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
            self.app.run(host=self.socket.ip, port=self.socket.port)
        self.thread = threading.Thread(target=do)
        self.thread.start()

    def kill(self):
        self.thread._stop()

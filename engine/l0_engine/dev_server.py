import html
import logging
import threading
from typing import Optional

from flask import Flask, request, jsonify

from engine.l1_agents import Identity
from engine.l2_models.context import Context, Entry
from engine.l3_aos import AOS
from holytools.network import Socket


# --------------------------------------------------------------

class DevServer:
    def __init__(self, socket : Socket = Socket.get_localhost(port=5000)):
        self.socket : Socket = socket
        self.app: Flask = Flask(__name__)
        self.thread: Optional[threading.Thread] = None
        self.context = self.get_example_context()

        @self.app.route(f'/context')
        def get_context_view() -> str:
            context_str = self.context.get_view(section_header=f'Agent context')
            escaped_context = html.escape(context_str)
            html_context = escaped_context.replace("\n", "<br>")
            html_context = f'<pre> {html_context} </pre>'
            return html_context

        @self.app.route('/update', methods=['POST'])
        def update():
            if not request.is_json:
                return jsonify({"error": "Missing JSON in request"}), 400

            data = request.get_json()
            s = data.get('data')
            self.context = Context.from_str(json_str=s)
            return jsonify({"received": s}), 200

    @staticmethod
    def get_example_context() -> Context:
        system_entry = Identity.GOTO().as_system_entry()
        hello_entry = Entry.user(msg=f'Hello there')
        basic_context = Context(entries=[system_entry, hello_entry])
        
        aos = AOS.terminal_only()
        aos_context = Context.from_aos(aos=aos)
        return aos_context + basic_context

    # -----------------------------------------------------

    def serve(self):
        logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        self.app.run(host=self.socket.ip, port=self.socket.port)

if __name__ == "__main__":
    server = DevServer()
    server.serve()
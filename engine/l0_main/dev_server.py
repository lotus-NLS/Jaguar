import html
import threading
from typing import Optional

from flask import Flask, request, jsonify

from engine.l1_agents import Identity
from engine.l2_models.language import Context, Entry
from engine.l3_aos import AOS
from holytools.userIO import MessageFormatter


# --------------------------------------------------------------

class DevMonitor:
    def __init__(self, ip : str, port : int):
        self.ip : str = ip
        self.port : int = port
        self.app: Flask = Flask(__name__)
        self.thread: Optional[threading.Thread] = None
        self.context = self.get_example_context()

        self.checkpoints : list[str] = []

        @self.app.route(f'/context')
        def get_context_view() -> str:
            return self.get_html()

        @self.app.route('/update', methods=['POST'])
        def update():
            data = request.get_data()
            s = data.decode()
            self.context = Context.from_str(json_str=s)
            return jsonify({"received": s}), 200

    @classmethod
    def localhost(cls, port : int = 5000):
        return cls(ip='127.0.0.1', port=port)

    @staticmethod
    def get_example_context() -> Context:
        system_entry = Identity.GOTO().as_system_entry()
        hello_entry = Entry.user(msg=f'Hello there')
        basic_context = Context(entries=[system_entry, hello_entry])
        
        aos = AOS.terminal_only()
        aos_context = Context.from_aos(aos=aos, with_update=False)
        return aos_context + basic_context

    def get_html(self) -> str:
        checkpoint_section = MessageFormatter.get_boxed_train(messages=self.checkpoints)
        context_str = self.context.get_view(section_header=f'Agent context')
        escaped_context = html.escape(context_str)
        html_code = escaped_context.replace("\n", "<br>")
        html_code = f'<pre> {checkpoint_section} {html_code} </pre>'
        return html_code

    # -----------------------------------------------------

    def serve(self):
        # logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        self.app.run(host=self.ip, port=self.port)

if __name__ == "__main__":
    server = DevMonitor.localhost()
    server.serve()
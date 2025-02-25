import html
from typing import Optional

from flask import Flask, request, jsonify

from engine.l1_agents import Identity
from engine.l2_models.generation.step import StepState
from engine.l2_models.language import Context, Entry
from engine.l3_aos import AOS
from holytools.userIO import MessageFormatter


# --------------------------------------------------------------

class DevMonitor:
    def __init__(self, ip : str, port : int):
        self.ip : str = ip
        self.port : int = port
        self.app: Flask = Flask(__name__)

        self.context : Context = self.get_example_context()
        self.checkpoints : dict[str, list[str]] = {}
        self.latest_session_uuid : Optional[str] = None

        @self.app.route(f'/context')
        def get_context_view() -> str:
            return self.get_html()

        @self.app.route('/update', methods=['POST'])
        def update():
            data = request.get_data()
            s = data.decode()
            step_state = StepState.from_str(json_str=s)
            self.latest_session_uuid = step_state.session_uuid
            self.context = step_state.generation_ctx
            if step_state.cpkt_label:
                self.checkpoints += [step_state.cpkt_label]

            return jsonify({"received": s}), 200

    @classmethod
    def localhost(cls, port : int = 5000):
        return cls(ip='127.0.0.1', port=port)


    def get_html(self) -> str:
        checkpoints = self.checkpoints.get(self.latest_session_uuid, None)
        ckpt_str = MessageFormatter.get_boxed_train(messages=checkpoints) if checkpoints else ''
        context_str = self.context.get_view(section_header=f'Agent context')
        plain_str = f'{ckpt_str}\n{context_str}'

        escaped_str = html.escape(plain_str)
        html_code = escaped_str.replace("\n", "<br>")
        html_code = f'<pre>{html_code}</pre>'
        return html_code

    # -----------------------------------------------------

    def serve(self):
        # logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        self.app.run(host=self.ip, port=self.port)

    @staticmethod
    def get_example_context() -> Context:
        system_entry = Identity.GOTO().as_system_entry()
        hello_entry = Entry.user(msg=f'Hello there')
        basic_context = Context(entries=[system_entry, hello_entry])

        aos = AOS.terminal_only()
        aos_context = Context.from_aos(aos=aos)
        return aos_context + basic_context


if __name__ == "__main__":
    server = DevMonitor.localhost()
    server.serve()
from __future__ import annotations
import html
from typing import Optional

from flask import Flask, request, jsonify

from engine.l2_models.generation.step import State, Report
from engine.l2_models.language import Context
from holytools.network import Endpoint
from holytools.userIO import MessageFormatter


# --------------------------------------------------------------

class DevMonitor:
    def __init__(self, ip : str, port : int):
        self.ip : str = ip
        self.port : int = port
        self.app: Flask = Flask(__name__)

        self.context_map : dict[str, Context] = {}
        self.ckpt_map : dict[str, list[str]] = {}
        self.latest_session_uuid : Optional[str] = None
        self.step_endpoint : Endpoint = self.make_endpopint(path=f'/step')
        self.report_endpoint : Endpoint = self.make_endpopint(path='/report')

        @self.app.route(f'/context')
        def get_context_view() -> str:
            return self.get_html()

        @self.app.route(self.step_endpoint.path, methods=['POST'])
        def log_update():
            s = request.get_data().decode()
            step_state = State.from_str(json_str=s)
            sess_uuid = step_state.sess_uuid

            self.latest_session_uuid = sess_uuid
            self.context_map[sess_uuid] = step_state.gen_ctx
            if not step_state.ckpt_label is None:
                if not sess_uuid in self.ckpt_map:
                    self.ckpt_map[sess_uuid] = []
                self.ckpt_map[sess_uuid].append(step_state.ckpt_label)

            return jsonify({"received": s}), 200

        @self.app.route(self.report_endpoint.path, methods=['POST'])
        def log_report():
            data = request.get_data().decode()
            report : Report = Report.from_str(json_str=data)
            icon = '✓' if report.is_successful else '✗'
            print(f'Report sucessful: {report.is_successful}, Icon = {icon}')

            if not report.sess_uuid in self.ckpt_map:
                self.ckpt_map[report.sess_uuid] = []
            self.ckpt_map[report.sess_uuid].append(icon)
            return jsonify({"received": data}), 200

    @classmethod
    def default(cls) -> DevMonitor:
        return cls.localhost(port=5000)

    @classmethod
    def localhost(cls, port : int) -> DevMonitor:
        return cls(ip='127.0.0.1', port=port)

    # -----------------------------------------------------

    def make_endpopint(self, path : str) -> Endpoint:
        return Endpoint(ip=self.ip, port=self.port, path=path)

    def serve(self):
        # logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        self.app.run(host=self.ip, port=self.port)

    def get_html(self) -> str:
        checkpoints = self.ckpt_map.get(self.latest_session_uuid, None)
        ckpt_str = MessageFormatter.get_boxed_train(messages=checkpoints) if checkpoints else ''
        context = self.context_map.get(self.latest_session_uuid, Context.get_example_context())
        context_str = context.get_view(f'Agent context')
        plain_str = f'{ckpt_str}\n{context_str}'

        escaped_str = html.escape(plain_str)
        html_code = escaped_str.replace("\n", "<br>")
        html_code = f'<pre>{html_code}</pre>'
        return html_code



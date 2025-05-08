from __future__ import annotations
import html
import time
from typing import Optional

from flask import Flask, request, jsonify, Response

from engine.l2_models.generation.step import State, Report
from engine.l2_models.language import Context
from holytools.network import Endpoint
from holytools.userIO import MessageFormatter

# --------------------------------------------------------------

class DefaultPorts:
    socket_port : 5001
    context_port : 5000


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
        self.html_code = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Data</title>
</head>
<body>
    <div id="data-container">
        <!-- Updates appear here -->
    </div>
    <script>
        const evtSource = new EventSource('/stream');
        evtSource.onmessage = function(event) {
            const dataContainer = document.getElementById('data-container');
            dataContainer.innerHTML = event.data;
        };
    </script>
</body>
</html>'''

        @self.app.route(f'/context')
        def get_context_view() -> str:
            return self.html_code

        @self.app.route(self.step_endpoint.path, methods=['POST'])
        def log_update():
            s = request.get_data().decode()
            step_state = State.from_str(json_str=s)
            sess_uuid = step_state.sess_uuid

            self.latest_session_uuid = sess_uuid
            self.context_map[sess_uuid] = step_state.post_context
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

        @self.app.route('/stream')
        def stream():
            return Response(self.ctx_stream(), mimetype='text/event-stream')

    @classmethod
    def default(cls) -> DevMonitor:
        return cls.localhost(port=DefaultPorts.context_port)

    @classmethod
    def localhost(cls, port : int) -> DevMonitor:
        return cls(ip='127.0.0.1', port=port)

    # -----------------------------------------------------

    def make_endpopint(self, path : str) -> Endpoint:
        return Endpoint(ip=self.ip, port=self.port, path=path)

    def serve(self):
        # logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        self.app.run(host=self.ip, port=self.port)

    def ctx_stream(self):
        while True:
            latest_data = self.get_latest_data()
            escaped_str = html.escape(latest_data)
            html_code = escaped_str.replace("\n", "<br>")
            formatted_html_code = f'<pre>{html_code}</pre>'
            yield f'data: {formatted_html_code}\n\n'
            time.sleep(1)  # You can adjust the sleep time as needed

    def get_latest_data(self):
        checkpoints = self.ckpt_map.get(self.latest_session_uuid, None)
        ckpt_str = MessageFormatter.get_boxed_train(messages=checkpoints) if checkpoints else ''
        context = self.context_map.get(self.latest_session_uuid, Context.get_example_context())
        context_str = context.get_view()
        return f'{ckpt_str}\n{context_str}'


if __name__ == "__main__":
    server = DevMonitor.default()
    server.serve()
from __future__ import annotations

import html
import time
from typing import Optional

from flask import Flask, request, jsonify, Response

from engine.l0_main.settings import DefaultPorts
from engine.l2_models.generation.step import State
from engine.l2_models.language import Context
from holytools.network import Endpoint


# --------------------------------------------------------------

class ContextMonitor:
    def __init__(self, ip : str, port : int):
        self.ip : str = ip
        self.port : int = port
        self.app: Flask = Flask(__name__)

        self.context_map : dict[str, Context] = {}
        self.latest_session_uuid : Optional[str] = None
        self.step_endpoint : Endpoint = self.make_endpopint(path=f'/step')
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
            return jsonify({"received": s}), 200

        @self.app.route('/stream')
        def stream():
            return Response(self.ctx_stream(), mimetype='text/event-stream')

    @classmethod
    def default(cls) -> ContextMonitor:
        return cls.localhost(port=DefaultPorts.context_port)

    @classmethod
    def localhost(cls, port : int) -> ContextMonitor:
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
        context = self.context_map.get(self.latest_session_uuid, Context.get_example_context())
        context_str = context.get_view()
        return f'{context_str}'


if __name__ == "__main__":
    server = ContextMonitor.default()
    server.serve()
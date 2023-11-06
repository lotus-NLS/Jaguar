import os
from flask import send_from_directory
from pyutils import DaemonThread

from engine import LotusEngine
from UI import LotusWebApp

# ---------------------------------------------------------

class LotusServer:
    def __init__(self):
        self.engine : LotusEngine = LotusEngine()
        self.web_app : LotusWebApp = LotusWebApp(title='Lotus')

        @self.web_app.route('/api/<path:filename>')
        def api_lib(filename):
            return send_from_directory('/api', filename)

        @self.web_app.route('/client/<path:filename>')
        def client_lib(filename):
            clientdir = os.path.join('UI', 'scripts/client')
            return send_from_directory(clientdir, filename)

    def run(self):
        self.launch_engine()
        self.launch_web_app()

    def launch_engine(self):
        def do_engine_run():
            self.engine.run()
        DaemonThread(target=do_engine_run).start()

    def launch_web_app(self):
        def do_web_app_run():
            self.web_app.run()
        DaemonThread(target=do_web_app_run()).start()

the_server = LotusServer()
the_server.run()
input('Press any key to quit')
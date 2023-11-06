import os
from flask import send_from_directory
from pyutils import DaemonThread

from engine import LotusEngine
from UI import LotusWebApp

# ---------------------------------------------------------

class LotusServer:
    def __init__(self):
        self.web_app: LotusWebApp = LotusWebApp(title='Lotus')
        self.engine : LotusEngine = LotusEngine(web_app=self.web_app)


        @self.web_app.route('/api/<path:filename>')
        def api_lib(filename):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            api_dir = os.path.join(current_dir, 'api')
            return send_from_directory(api_dir, filename)

        @self.web_app.route('/client/<path:filename>')
        def client_lib(filename):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            clientdir = os.path.join(current_dir,'UI', 'scripts/client')
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
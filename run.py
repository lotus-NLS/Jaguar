import os
from flask import send_from_directory
from pyutils import DaemonThread

from engine import LotusEngine
from deploy import LotusWebApp

# ---------------------------------------------------------

class LotusServer:
    def __init__(self):
        self.web_app: LotusWebApp = LotusWebApp(title='Lotus')
        self.engine : LotusEngine = LotusEngine(web_app=self.web_app)
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        @self.web_app.route('/api/<path:filename>')
        def api_lib(filename):
            api_dir = os.path.join(self.current_dir, 'api')
            return send_from_directory(api_dir, filename)

        @self.web_app.route('/lib/<path:filename>')
        def client_lib(filename):
            clientdir = os.path.join(self.current_dir, 'deploy', 'interaction', 'lib')
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
            self.web_app.run(host='0.0.0.0', port=5000)
        DaemonThread(target=do_web_app_run()).start()


the_server = LotusServer()
the_server.run()
input('Press any key to quit')
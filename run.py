import os
from flask import send_from_directory

from engine import LotusEngine
from UI import LotusWebApp

# ---------------------------------------------------------

class LotusServer:
    def __init__(self):
        self.engine : LotusEngine = LotusEngine()
        self.web_app : LotusWebApp = LotusWebApp(title='Lotus')

        @self.web_app.route('/api/<path:filename>')
        def api_lib(filename):
            parent_directory = os.path.dirname(self.web_app.directory_path)
            api_directory = os.path.join(parent_directory, 'api')
            return send_from_directory(api_directory, filename)

        @self.web_app.route('/client/<path:filename>')
        def client_lib(filename):
            clientdir = os.path.join(self.web_app.directory_path, 'scripts/client')
            return send_from_directory(clientdir, filename)

        self.web_app.run(debug=True, use_reloader=False)
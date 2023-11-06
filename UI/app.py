import os
from pywebdev.devkit import PyWebApp

from flask_socketio import SocketIO
from flask import send_from_directory

# ----------------------------------------------

class ChatHTML(PyWebApp):
    def add_body_content(self):
        # Chat window
        # chat_window_style = Style(height='300px', border='1px solid #ccc', overflow='auto')
        # self.add_tag(tag_name='div', id='chat-window', style=chat_window_style)
        with self.add_tag('div', id='chat-window', style='height:300px; border:1px solid #ccc; overflow:auto;'):
            self.generate_text('')

        # Text and send button
        self.add_text_field(the_id='text_bar')
        self.add_button(the_id='Send', value ='Send')

        # Chat Interactivity
        self.add_python_script(relPath='scripts/send.py')
        self.add_python_script(relPath='scripts/receive.py')

# ----------------------------------------------
# Run webapp

app = ChatHTML(title='This new app')
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/api/<path:filename>')
def api_lib(filename):
    parent_directory = os.path.dirname(app.directory_path)
    api_directory = os.path.join(parent_directory, 'api')
    return send_from_directory(api_directory, filename)

@app.route('/client/<path:filename>')
def client_lib(filename):
    clientdir = os.path.join(app.directory_path, 'scripts/client')
    return send_from_directory(clientdir, filename)


app.run(debug=True, use_reloader=False)

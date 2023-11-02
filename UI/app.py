from pywebdev.devkit import PyWebApp, InputType, Style
from api import LotusServer
from flask_socketio import SocketIO

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
        self.add_python_script(relPath='scripts/send_routine.py')
        self.add_python_script(relPath='scripts/socketio.py')


if __name__ == '__main__':
    app = ChatHTML(title='This new app')
    socketio = SocketIO(app, cors_allowed_origins='*')


    @socketio.on('connect')
    def handle_connect():
        print('Client connected')


    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')


    @socketio.on('message')
    def handle_message(msg):
        print('Received message:', msg)

    app.run(debug=True)

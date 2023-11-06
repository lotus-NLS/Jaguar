import time
from pyutils import InputWaiter
from flask import jsonify,request, Response
from typing import Optional

from api.classes.api import APIMessage
from api.classes.language import Entry
from pywebdev import PyWebApp
# ----------------------------------------------

class EngineIO:
    _instance = None
    _is_initialized = False


    def __new__(cls, *args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, web_app : Optional[PyWebApp] = None):
        if not EngineIO._is_initialized:
            self.web_app : PyWebApp = web_app
            self._incoming_entry_waiter : InputWaiter = InputWaiter()
            self._incoming_bool_waiter : InputWaiter = InputWaiter()

            @self.web_app.route('/item/', methods=['POST'])
            def create_item():
                data = request.json
                return jsonify({"message": "Item received", "data": data})

            @self.web_app.route('/stream')
            def stream():
                def event_stream():
                    while True:
                        yield 'event: customEventName\ndata: Hello\n\n'
                        time.sleep(1)
                    pass

                return Response(event_stream(), mimetype='text/event-stream')

            EngineIO._is_initialized = True

    # ----------------------------------------------
    # Handlers

    def _user_data_handler(self, lotus_msg: APIMessage) -> str:
        if not lotus_msg.get_entry() is None:
            self._incoming_entry_waiter.write(lotus_msg.get_entry())

        if lotus_msg.get_bool_content() is None:
            self._incoming_bool_waiter.write(lotus_msg.get_bool_content())

        return 'message ok'

    # ----------------------------------------------
    # API

    # TODO
    def post_engine_message(self,msg : str):
        pass

    def get_user_entry(self) -> Entry:
        self._incoming_entry_waiter.clear()
        user_entry = self._incoming_entry_waiter.read()
        print(f'Entry received')
        return user_entry


    def get_confirmation(self):
        self._incoming_bool_waiter.clear()
        pass
from pyutils import InputWaiter
from flask import Response, request
from typing import Optional
from queue import Queue

from api import APIMessage, Entry, Ends, DialogueRole
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
        if not EngineIO._is_initialized and web_app is None:
            raise ValueError('Cannot instantiate EngineIO without associated webapp')

        if EngineIO._is_initialized:
            return

        self._web_app : PyWebApp = web_app
        self._outpoing_entry_queue : Queue[Entry] = Queue()
        self._incoming_entry_waiter : InputWaiter = InputWaiter()
        self._incoming_bool_waiter : InputWaiter = InputWaiter()

        self._web_app.route(f'/{Ends.agent_data.identifier}')(self._engine_datastream_handler)
        self._web_app.route(f'/{Ends.user_data.identifier}', methods=[Ends.user_data.get_req_type()])(self._user_data_handler)

        EngineIO._is_initialized = True

    # ----------------------------------------------
    # Handlers

    def _engine_datastream_handler(self):
        def event_stream():
            while True:
                new_entry = self._outpoing_entry_queue.get()
                yield f'event: customEventName\ndata: {new_entry.to_str()}\n\n'
            pass

        return Response(event_stream(), mimetype='text/event-stream')

    def _user_data_handler(self) -> str:
        try:
            msg_content = request.get_json()['msg_content']
            lotus_msg = APIMessage.from_str(s=msg_content)
            if not lotus_msg.get_entry() is None:
                self._incoming_entry_waiter.write(lotus_msg.get_entry())

            if lotus_msg.get_bool_content() is None:
                self._incoming_bool_waiter.write(lotus_msg.get_bool_content())

            status_msg = 'message ok'

        except Exception as e:
            status_msg = f'Failed to parse message due to error: {e}'

        return status_msg


    # ----------------------------------------------
    # API

    def post_engine_entry(self, entry : Entry):
        self._outpoing_entry_queue.put(entry)


    def post_engine_msg(self, msg : str):
        entry = Entry(msg=msg,role=DialogueRole.agent_role())
        self._outpoing_entry_queue.put(entry)


    def get_user_entry(self) -> Entry:
        self._incoming_entry_waiter.clear()
        user_entry = self._incoming_entry_waiter.read()
        # print(f'Entry received')
        return user_entry


    def get_confirmation(self):
        self._incoming_bool_waiter.clear()
        pass
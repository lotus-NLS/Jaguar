from typing import Optional
from flask import Response, request
from queue import Queue
from api import Ends, DefaultNetwork, Entry, APIMessage
from hollarek.events import InputWaiter
from flask import Flask
from flask_cors import CORS
from hollarek.tmpl import Singleton
# ----------------------------------------------


class EngineIO(Flask, Singleton):
    def __init__(self, ip : Optional[str] = None, port : Optional[int] = None):
        if EngineIO.is_initialized:
            return

        Flask.__init__(self, import_name=__name__)
        Singleton.__init__(self)

        CORS(self)
        self.ip : str = ip if ip else DefaultNetwork.ip_engine
        self.port : int = port if port else DefaultNetwork.port_engine

        self._outgoing_entry_queue : Queue[Entry] = Queue()
        self._incoming_entry_waiter : InputWaiter = InputWaiter()
        self._incoming_bool_waiter : InputWaiter = InputWaiter()

        self.route(f'/{Ends.engine_data.identifier}')(self._get_stream)
        self.route(f'/{Ends.user_data.identifier}', methods=[Ends.user_data.get_req_type()])(self._process_user)

    def launch(self):
        self.run(host=self.ip, port=self.port)

    # ----------------------------------------------
    # callbacks

    def _get_stream(self):
        def event_stream():
            while True:
                new_entry = self._outgoing_entry_queue.get()
                yield f'data: {new_entry.serialize_as_str()}\n\n'

        return Response(event_stream(), mimetype='text/event-stream')


    def _process_user(self) -> str:
        try:
            msg_content = request.get_json()['msg_content']
            lotus_msg = APIMessage.from_serialized_str(s=msg_content)
            if not lotus_msg.get_entry() is None:
                self._incoming_entry_waiter.write(lotus_msg.get_entry())
            status_msg = 'message ok'

        except Exception as e:
            status_msg = f'Failed to parse message due to error: {e}'

        return status_msg


    # ----------------------------------------------
    # API

    def send(self, entry : Entry):
        self._outgoing_entry_queue.put(entry)


    def get_entry(self) -> Entry:
        self._incoming_entry_waiter.clear()
        user_entry = self._incoming_entry_waiter.read()
        return user_entry


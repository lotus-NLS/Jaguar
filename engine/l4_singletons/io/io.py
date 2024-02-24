# from typing import Optional
# from flask import Response, request
# from queue import Queue
#
#
# from flask import Flask
# from flask_cors import CORS
# # ----------------------------------------------
#
# class EngineIO(Flask):
#     _instance = None
#     _is_initialized = False
#
#     def __new__(cls, *args,**kwargs):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#
#         return cls._instance
#
#     def __init__(self, ip : Optional[str] = None, port : Optional[int] = None):
#         if EngineIO._is_initialized:
#             return
#
#         super().__init__(import_name=__name__)
#         CORS(self)
#
#         self.ip : Optional[str] = ip
#         self.port : Optional[int] = port
#
#         self._outgoing_entry_queue : Queue[Entry] = Queue()
#         self._incoming_entry_waiter : InputWaiter = InputWaiter()
#         self._incoming_bool_waiter : InputWaiter = InputWaiter()
#
#         self.route(f'/{Ends.engine_data.identifier}')(self._engine_datastream_handler)
#         self.route(f'/{Ends.user_data.identifier}', methods=[Ends.user_data.get_req_type()])(self._user_data_handler)
#
#         EngineIO._is_initialized = True
#
#
#     def launch(self):
#         def do_run():
#             the_ip = self.ip if not self.ip is None else DefaultNetwork.ip_engine
#             the_port = self.port if not self.port is None else DefaultNetwork.port_engine
#             self.run(host=the_ip, port=the_port)
#         DaemonThread(target=do_run).start()
#
#     # ----------------------------------------------
#     # Handlers
#
#     def _engine_datastream_handler(self):
#         def event_stream():
#             while True:
#                 new_entry = self._outgoing_entry_queue.get()
#                 yield f'data: {new_entry.serialize_as_str()}\n\n'
#
#         return Response(event_stream(), mimetype='text/event-stream')
#
#
#     def _user_data_handler(self) -> str:
#         try:
#             msg_content = request.get_json()['msg_content']
#             lotus_msg = APIMessage.from_serialized_str(s=msg_content)
#             if not lotus_msg.get_entry() is None:
#                 self._incoming_entry_waiter.write(lotus_msg.get_entry())
#
#             if lotus_msg.get_bool_content() is None:
#                 self._incoming_bool_waiter.write(lotus_msg.get_bool_content())
#
#             status_msg = 'message ok'
#
#         except Exception as e:
#             status_msg = f'Failed to parse message due to error: {e}'
#
#         return status_msg
#
#
#     # ----------------------------------------------
#     # API
#
#     def post_engine_entry(self, entry : Entry):
#         self._outgoing_entry_queue.put(entry)
#
#
#     def get_user_entry(self) -> Entry:
#         self._incoming_entry_waiter.clear()
#         user_entry = self._incoming_entry_waiter.read()
#         return user_entry
#
#
#     def get_confirmation(self):
#         self._incoming_bool_waiter.clear()
#         pass
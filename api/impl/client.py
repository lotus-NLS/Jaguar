from typing import Optional
from api.base.io_module import LotusIO
from api.base.api_types import APIMessage, DefaultNetwork, Ends
from api.base.language_types import Entry
from flask_socketio import SocketIO

# ----------------------------------------------

class LotusClientIO(LotusIO):
    _instance = None
    _is_initialized = False

    def __new__(cls, *args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance
    
    def __init__(self, socketio : Optional[SocketIO],
                 ip_addr : str = DefaultNetwork.ip,
                 port : int = DefaultNetwork.client_port):
        super().__init__(ip_addr=ip_addr,port=port)
        self.agent_data_endpoint = self.handle_endpoint(endpoint=Ends.agent_data, handler=self.agent_data_handler)
        self.the_socket : SocketIO = socketio

    # ----------------------------------------------
    # Handlers

    def agent_data_handler(self,lotus_msg : APIMessage) -> None:
        entry = lotus_msg.get_entry()
        self.the_socket.emit('agentmessage', (entry.get_content(),entry.flags.is_entry_end))
        print(f'Client heard: {entry.get_content()}')

    # ----------------------------------------------
    # API

    def send_user_entry(self, entry : Entry) -> None:
        payload = APIMessage(entry_str=entry.to_str())
        self._communicate(endpoint=Ends.user_data, payload=payload)


    def send_confirmation(self, is_confirmed : bool):
        self._communicate(endpoint=Ends.user_data, payload=APIMessage(bool_content=is_confirmed))


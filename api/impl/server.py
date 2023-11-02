from pyutils import InputWaiter

from api.base.io_module import LotusIO
from api.base.api_types import APIMessage, NetworkQuantities, Ends, EntryModel
from api.base.language_types import Entry, DialogueRole


# ----------------------------------------------

class LotusServer(LotusIO):
    _instance = None
    _is_initialized = False


    def __new__(cls, *args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance


    def __init__(self, ip_addr : str = NetworkQuantities.default_ip, port : int = 8000):
        if not LotusServer._is_initialized:
            super().__init__(ip_addr=ip_addr,port=port)
            self.user_data_endpoint = self.handle_endpoint(endpoint=Ends.user_data, handler=self._user_data_handler)
            self._incoming_entry_waiter : InputWaiter = InputWaiter()
            self._incoming_bool_waiter : InputWaiter = InputWaiter()

            LotusServer._is_initialized = True

    # ----------------------------------------------
    # Handlers

    def _user_data_handler(self, lotus_msg: APIMessage) -> str:
        if not lotus_msg.get_entry_model() is None:
            entry_model = lotus_msg.get_entry_model()
            self._incoming_entry_waiter.write(Entry.from_model(entry_model=entry_model))

        if lotus_msg.get_bool_content() is None:
            self._incoming_bool_waiter.write(lotus_msg.get_bool_content())

        return 'message ok'


    # ----------------------------------------------
    # API

    def post_engine_message(self, msg_content : str) -> None:
        entry = Entry(msg=msg_content,role=DialogueRole.agent_role())
        the_msg = APIMessage(entry_model=EntryModel.from_entry(entry=entry))
        self._communicate(endpoint=Ends.agent_data, payload=the_msg)

    
    def get_user_entry(self) -> Entry:
        self._incoming_entry_waiter.clear()
        user_entry = self._incoming_entry_waiter.read()
        print(f'Entry received')
        return user_entry


    def get_confirmation(self):
        self._incoming_bool_waiter.clear()
        pass

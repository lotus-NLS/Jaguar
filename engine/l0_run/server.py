from pyutils import InputWaiter
from fastapi import FastAPI, Request
import uvicorn


from api.classes.api import APIMessage
from api.constants.network import DefaultNetwork
from api.classes.language import Entry
from pyutils import DaemonThread

# ----------------------------------------------

class LotusServerIO:
    _instance = None
    _is_initialized = False


    def __new__(cls, *args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def start(self):
        def do_start():
            uvicorn_config = uvicorn.Config(app=self.app, host=self.ip_addr, port=self.port)
            server = uvicorn.Server(config=uvicorn_config)
            server.run()
        DaemonThread(target=do_start).start()


    def __init__(self, ip_addr : str = DefaultNetwork.ip, port : int = 8000):
        if not LotusServerIO._is_initialized:
            self.app = FastAPI()
            self.ip_addr: str = ip_addr
            self.port: int = port

            self._incoming_entry_waiter : InputWaiter = InputWaiter()
            self._incoming_bool_waiter : InputWaiter = InputWaiter()

            @self.app.post("/item/")
            async def create_item(request: Request):
                data = await request.json()
                return {"message": "Item received", "data": data}

            LotusServerIO._is_initialized = True

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

    def get_user_entry(self) -> Entry:
        self._incoming_entry_waiter.clear()
        user_entry = self._incoming_entry_waiter.read()
        print(f'Entry received')
        return user_entry


    def get_confirmation(self):
        self._incoming_bool_waiter.clear()
        pass
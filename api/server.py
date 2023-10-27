import uvicorn
from fastapi import FastAPI, Query
from .base_types import ReqType, Message

# ----------------------------------------------
class LotusAPI_Server:
    def __init__(self, ip_addr : str, port : int):
        self.app = FastAPI()
        self.ip_add : str = ip_addr
        self.port : int = port
        self.user_messages = {}  # In-memory data structure to hold messages

        self.endpoints = []

    def make_endpoint(self, funct : callable, req_type : ReqType):
        decorator = self.app.get if req_type == ReqType.get() else self.app.post
        funct_name = funct.__name__
        decorator(f'/{funct_name}/')(funct)


    def initialize(self, user_id: int):
        self.user_messages[user_id] = []
        return {"message": f"User {user_id} initialized."}

    def receive_message(self, user_id: int):
        messages = self.user_messages.get(user_id, [])
        return {"user_id": user_id, "messages": messages}

    def post_message_get(self, user_id: int, content: str = Query(..., alias="message_content")):
        if user_id in self.user_messages:
            self.user_messages[user_id].append(content)
            return {"message": f"Message '{content}' added for user {user_id}."}
        else:
            return {"error": f"User {user_id} not initialized."}

    def post_message(self, user_id: int, message: Message):
        if user_id in self.user_messages:
            self.user_messages[user_id].append(message.content)
            return {"message": f"Message '{message.content}' added for user {user_id}."}
        else:
            return {"error": f"User {user_id} not initialized."}

    def run(self):
        uvicorn_config = uvicorn.Config(app=self.app, host=self.ip_add, port=self.port)
        server = uvicorn.Server(config=uvicorn_config)
        server.run()


# Create an instance of the class and get the FastAPI app object
# my_app = LotusAPI_Server(ip_addr='127.0.0.1',port=8000)
# app = my_app.app


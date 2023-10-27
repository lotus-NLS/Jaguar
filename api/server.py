import uvicorn
from fastapi import FastAPI
from api.base_types import ReqType, APIMessage
# ----------------------------------------------



class LotusAPI_Server:
    def __init__(self, ip_addr : str, port : int):
        self.app = FastAPI()
        self.ip_add : str = ip_addr
        self.port : int = port
        self.user_messages = {}  # In-memory data structure to hold messages

        self.make_endpoint(funct=self.initialize,req_type=ReqType.get())
        self.make_endpoint(funct=self.receive_message,req_type=ReqType.get())
        self.make_endpoint(funct=self.message_get, req_type=ReqType.get())

    def make_endpoint(self, funct : callable, req_type : ReqType):
        decorator = self.app.get if req_type == ReqType.get() else self.app.post
        decorator(f'/{funct.__name__}/')(funct)

    # ----------------------------------------------

    def initialize(self, lotus_msg: APIMessage):
        user_id = lotus_msg.user_id
        self.user_messages[user_id] = []
        return {"message": f"User {user_id} initialized."}

    def receive_message(self, lotus_msg: APIMessage):
        user_id = lotus_msg.user_id
        messages = self.user_messages.get(user_id, [])
        return {"user_id": user_id, "messages": messages}

    def message_get(self, lotus_msg: APIMessage):
        user_id = lotus_msg.user_id
        content = lotus_msg.msg_content
        if user_id in self.user_messages:
            self.user_messages[user_id].append(content)
            return {"message": f"Message '{content}' added for user {user_id}."}
        else:
            return {"error": f"User {user_id} not initialized."}

    def post_message(self, lotus_msg: APIMessage):
        user_id = lotus_msg.user_id
        content = lotus_msg.msg_content
        if user_id in self.user_messages:
            self.user_messages[user_id].append(content)
            return {"message": f"Message '{content}' added for user {user_id}."}
        else:
            return {"error": f"User {user_id} not initialized."}

    # ----------------------------------------------

    def run(self):
        uvicorn_config = uvicorn.Config(app=self.app, host=self.ip_add, port=self.port)
        server = uvicorn.Server(config=uvicorn_config)
        server.run()


def main():
    # Create an instance of the class and get the FastAPI app object
    my_app = LotusAPI_Server(ip_addr='127.0.0.1', port=8000)
    my_app.run()

if __name__ == '__main__':
    main()

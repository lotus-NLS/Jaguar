from browser import window, ajax

from api import APIMessage
import json

from api import Ends, Endpoint
# ----------------------------------------------

class Client:
    def __init__(self, ip : str, port : int):
        self.ip : str = ip
        self.port : int = port
        self.base_url : str = f"http://{ip}:{port}"


    def send_api_msg(self, api_message: APIMessage):
        self._request(endpoint=Ends.user_data,
                      data=json.dumps({"msg_content": api_message.serialize_as_str()}))
        # print('I sent the message')


    @staticmethod
    def on_complete(req) -> str:
        if req.status == 200 or req.status == 0:
            return "Message sent successfully"
        else:
            return "Error sending message"


    def _request(self, endpoint : Endpoint, data : str):
        method = endpoint.get_req_type()
        url = f"{self.base_url}/{endpoint.identifier}"

        req = ajax.Ajax()
        req.open(method, url, True)
        req.bind('complete', self.on_complete)

        if data and method == 'POST':
            req.set_header('content-type', 'application/json')
            req.send(data)
        else:
            req.send()

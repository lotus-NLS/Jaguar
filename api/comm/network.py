from .endpoint import Endpoint, Socket, Method


class Network:
    def __init__(self, webapp_socket : Socket = Socket('127.0.0.1', port = 5000),
                       engine_socket : Socket = Socket('127.0.0.1', port = 5001)):
        super().__init__()
        self.webapp_socket : Socket =  webapp_socket
        self.engine_socket : Socket =  engine_socket
        self.post_endpoint : Endpoint = Endpoint(name='post', method=Method.POST, socket=engine_socket)



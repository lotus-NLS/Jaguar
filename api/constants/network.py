from api.classes.api import Endpoint, ReqType


class DefaultNetwork:
    ip : str = '127.0.0.1'
    engine_port : int = 8000
    client_port : int = 8001


class Ends:
    user_data = Endpoint(name='user_data_endpoint', req_type=ReqType.post())

    agent_data = Endpoint(name='agent_data_endpoint', req_type=ReqType.get())

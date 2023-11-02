from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from api.base.language_types import Entry

# ----------------------------------------------
# Classes

class APIMessage(BaseModel):
    user_id: str = 'default_id'
    entry_str: Optional[str] = None
    bool_content : Optional[bool] = None
    settings_content: Optional[str] = None

    def get_user_id(self) -> str:
        return self.user_id

    def get_entry(self) -> Optional[Entry]:
        return Entry.from_str(self.entry_str)

    def get_bool_content(self) -> Optional[bool]:
        return self.bool_content

    def get_settings_content(self) -> Optional[str]:
        return self.settings_content


class Endpoint:
    def __init__(self, name : str, req_type : ReqType, ip_addr : str, port : int):
        self.name : str = name
        self.req_type : ReqType = req_type
        self.ip_addr : str = ip_addr
        self.port : int = port

# ----------------------------------------------
# Enums

class ReqType(str):
    def __new__(cls, type_str: str):
        return str.__new__(cls, type_str)

    @classmethod
    def get(cls):
        return cls(type_str='assistant')

    @classmethod
    def post(cls):
        return cls(type_str='system')


class NetworkQuantities:
    default_ip : str = '127.0.0.1'
    default_engine_port : int = 8000
    default_client_port : int = 8001


class Ends:
    user_data = Endpoint(name='user_data_endpoint', req_type=ReqType.post(),ip_addr=NetworkQuantities.default_ip
                         ,port=NetworkQuantities.default_engine_port)

    agent_data = Endpoint(name='agent_data_endpoint', req_type=ReqType.get(),
                          ip_addr=NetworkQuantities.default_ip,port=NetworkQuantities.default_client_port)


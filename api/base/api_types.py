from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from api.base.language_types import Entry

# ----------------------------------------------
# Classes

class EntryModel(BaseModel):
    role: str
    content: str
    flags: Optional[list[str]] = None

    @classmethod
    def from_entry(cls, entry: Entry):
        return cls(role=entry.get_role(), content=entry.get_content(), flags=entry.flags)


class APIMessage(BaseModel):
    user_id: str = 'default_id'
    entry_model: Optional[EntryModel] = None
    bool_content : Optional[bool] = None
    settings_content: Optional[str] = None


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


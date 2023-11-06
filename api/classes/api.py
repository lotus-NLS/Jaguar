from typing import Optional
from api.classes.language import Entry

# ----------------------------------------------
# Classes

class APIMessage:
    def __init__(self):
        self.user_id = 'default_id'
        self.entry_str : Optional[str] = None
        self.bool_content : Optional[bool] = None
        self.settings_content : Optional[str] = None

    def get_user_id(self) -> str:
        return self.user_id

    def get_entry(self) -> Entry:
        return Entry.from_str(self.entry_str)

    def get_bool_content(self) -> bool:
        return self.bool_content

    def get_settings_content(self) -> str:
        return self.settings_content


class ReqType(str):
    def __new__(cls, type_str: str):
        return str.__new__(cls, type_str)

    @classmethod
    def get(cls):
        return cls(type_str='assistant')

    @classmethod
    def post(cls):
        return cls(type_str='system')


class Endpoint:
    def __init__(self, name : str, req_type : ReqType, ip_addr : str, port : int):
        self.name : str = name
        self.req_type : ReqType = req_type
        self.ip_addr : str = ip_addr
        self.port : int = port

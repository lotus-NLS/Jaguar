from typing import Optional
from api.classes.language import Entry
from .serializable import Serializable

# ----------------------------------------------
# Classes

class APIMessage(Serializable):
    def __init__(self, entry : Entry, bool_content : Optional[bool] = None, settings_content : Optional[dict] = None):
        self.user_id = 'default_id'
        self.entry_str : Optional[str] = entry.to_str()
        # self.bool_content : Optional[str] = bool_content.to_str() if not bool_content is None else None
        # self.settings_content : Optional[str] = settings_content.to_str() if not settings_content is None else None
        self.bool_content : Optional[str] = bool_content
        self.settings_content : Optional[str] = settings_content

    def get_user_id(self) -> str:
        return self.user_id

    def get_entry(self) -> Entry:
        return Entry.from_str(self.entry_str)

    # TODO
    @staticmethod
    def get_bool_content(self) -> bool:
        _ = self
        # return self.bool_content.from_str()
        return True

    def get_settings_content(self) -> str:
        return self.settings_content


class ReqType(str):
    def __new__(cls, type_str: str):
        return str.__new__(cls, type_str)

    @classmethod
    def get(cls):
        return cls(type_str='GET')

    @classmethod
    def post(cls):
        return cls(type_str='POST')


class Endpoint:
    def __init__(self, name : str, req_type : ReqType):
        self.identifier : str = name
        self.req_type : ReqType = req_type

    def get_req_type(self) -> str:
        return str(self.req_type)

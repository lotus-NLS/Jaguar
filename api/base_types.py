from typing import Optional
from pydantic import BaseModel, Field

class APIMessage(BaseModel):
    user_id: str
    msg_content: Optional[str] = None
    # settings_content: Optional[str] = None


class ReqType(str):
    def __new__(cls, type_str: str):
        return str.__new__(cls, type_str)

    @classmethod
    def get(cls):
        return cls(type_str='assistant')

    @classmethod
    def post(cls):
        return cls(type_str='system')

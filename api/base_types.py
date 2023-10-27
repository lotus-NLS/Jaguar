from typing import Optional
from pydantic import BaseModel

class APIMessage(BaseModel):
    user_id: str
    msg_content: Optional[str] = None
    settings_content: Optional[str] = None

    def __init__(self, user_id: str = 'abcd', msg_content: Optional[str] = None, settings_content : Optional[str] = None):
        # !! The kwargs name have to match the attributes defined above
        # it would be great if there was some way around that redundancy but I dont think there is
        super().__init__(user_id=user_id, msg_content=msg_content,settings_content=settings_content)


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
    default_port : int = 8000

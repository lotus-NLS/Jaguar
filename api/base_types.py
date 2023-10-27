from pydantic import BaseModel, Field

class Message(BaseModel):
    type: str = Field(..., description="The type of message (e.g., 'initialize', 'receive_message')")
    content: str = Field(None, description="The message content")
    arguments: dict = Field({}, description="Additional arguments for the request")


class ReqType(str):
    def __new__(cls, type_str : str):
        return str.__new__(cls, type_str)

    @classmethod
    def get(cls):
        return cls(type_str='assistant')

    @classmethod
    def post(cls):
        return cls(type_str='system')
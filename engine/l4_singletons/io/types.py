from abc import ABC, abstractmethod
from typing import Iterator
from dataclasses import dataclass
from enum import Enum
from typing import Optional
# --------------------------------------------

class TextStream(ABC, Iterator[str]):
    @abstractmethod
    def __iter__(self) -> 'TextStream':
        pass

    @abstractmethod
    def __next__(self) -> str:
        pass


class QueryType(Enum):
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"

@dataclass
class UserResponse:
    msg : Optional[str] = None
    decision : Optional[bool] = None

    def __post_init__(self):
        if self.msg is None and self.decision is None:
            raise ValueError('At least one of msg or decision must be provided')

@dataclass
class UserQuery:
    msg : str
    query_type : QueryType

    @abstractmethod
    def get_query_display(self):
        pass

    def send_response(self, user_response : UserResponse):
        pass

    def get_response(self) -> UserResponse:
        pass

@dataclass
class ServerResponse:
    user_query : Optional[UserQuery]
    text_stream : Optional[TextStream]


    def __post_init__(self):
        if self.user_query is None and self.text_stream is None:
            raise ValueError('At least one of user_query or text_stream must be provided')


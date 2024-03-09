from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from collections.abc import Iterator
from queue import Queue
from typing import Optional

from api import Entry
# --------------------------------------------

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


class QueryType(Enum):
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"

class TextStream(Iterator[str], ABC):
    pass

class FailedTextStream(TextStream):
    def __init__(self, message: str = "Response failed"):
        self.message = message
        self.has_been_read = False

    def __next__(self) -> str:
        if self.has_been_read:
            raise StopIteration
        self.has_been_read = True
        return self.message

    def __iter__(self) -> Iterator[str]:
        return self

@dataclass
class Response:
    text_stream : Optional[TextStream]
    user_query: Optional[UserQuery] = None

    def __post_init__(self):
        if self.user_query is None and self.text_stream is None:
            raise ValueError('At least one of user_query or text_stream must be provided')

    @classmethod
    def failed(cls):
        return cls(text_stream=FailedTextStream(), user_query=None)


class TaskQueue(Queue):
    def __init__(self):
        super().__init__()
        self.queued_items : set = set()
        self.work_mode_enabled : bool = False

    def put(self, item : Task, block=True, timeout=None):
        super().put(item, block, timeout)
        self.queued_items.add(item)

    def get(self, block=True, timeout=None) -> Task:
        new_task = super().get(block, timeout)
        self.queued_items.remove(new_task)
        return new_task

    def get_work_task_present(self) -> bool:
        return any(task.is_mandate_task() for task in self.queued_items)

    def dialogue_task_is_enqueued(self) -> bool:
        return any(task.is_dialogue_task() for task in self.queued_items)


class Task:
    def __init__(self, new_entries : list[Entry] = None, required_tool_name : Optional[str] = None):
        self.new_entries : list[Entry] = new_entries if new_entries else []
        self.required_tool_name : Optional[str] = required_tool_name
        self.skip_feedback : bool = False if self.required_tool_name is None else True
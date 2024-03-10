from __future__ import annotations

from hollarek.logging import Loggable, LogLevel
import queue
from collections.abc import Iterator
from queue import Queue
from typing import Optional

from api import Entry
# --------------------------------------------

# @dataclass
# class UserResponse:
#     msg : Optional[str] = None
#     decision : Optional[bool] = None
#
#     def __post_init__(self):
#         if self.msg is None and self.decision is None:
#             raise ValueError('At least one of msg or decision must be provided')
#
#
# @dataclass
# class UserQuery:
#     msg : str
#     query_type : QueryType
#
#     @abstractmethod
#     def get_query_display(self):
#         pass
#
#     def send_response(self, user_response : UserResponse):
#         pass
#
#     def get_response(self) -> UserResponse:
#         pass
#
#
# class QueryType(Enum):
#     STRING = "STRING"



class TextPipeline(Queue):
    def _init(self, maxsize):
        super().__init__(maxsize)

    def put(self, item : str, *args, **kwargs):
        if not isinstance(item, str):
            raise TypeError("Only strings are allowed in the TextQueue.")
        super().put(item, *args, **kwargs)

    def get(self, *args, **kwargs) -> str:
        item = super().get(*args, **kwargs)
        if not isinstance(item, str):
            raise TypeError("Only strings should be in the TextQueue, found: {}".format(type(item)))
        return item

    def stop(self):
        self.put(Response.stop_token)


# class FailedTextStream(TextStream):
#     def __init__(self, message: str = "Response failed"):
#         self.message = message
#         self.has_been_read = False
#
#     def __next__(self) -> str:
#         if self.has_been_read:
#             raise StopIteration
#         self.has_been_read = True
#         return self.message
#
#     def __iter__(self) -> Iterator[str]:
#         return self



class Response(Loggable):
    stop_token = '⊥'

    def __init__(self, text_queue : Queue[str]):
        super().__init__()
        self.text_queue : TextPipeline = text_queue

    def get_text_stream(self) -> Iterator[str]:
        timeout = 10
        while True:
            try:
                text = self.text_queue.get(timeout=timeout)
            except queue.Empty:
                self.log(f'Text queue timed out after {timeout}s', level=LogLevel.WARNING)
                break
            except Exception as e:
                self.log(f'Error in getting text from queue: {e}', level=LogLevel.ERROR)
                break
            if text == self.stop_token:
                break
            if not text:
                continue
            yield text


    @classmethod
    def failed(cls):
        pass


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
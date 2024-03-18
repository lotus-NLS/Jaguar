from __future__ import annotations

from queue import Queue
from typing import Optional

from api import Entry
from engine.l3_models import Options, CallOptions


class Task:
    def __init__(self, new_entries : list[Entry] = None, required_tool_name : Optional[str] = None):
        self.new_entries : list[Entry] = new_entries if new_entries else []
        self.selected_tool : Optional[str] = required_tool_name
        self.skip_feedback : bool = False if self.selected_tool is None else True

    @classmethod
    def make_default(cls, msg : str):
        return cls(new_entries=[Entry.as_user(msg=msg)])

    def get_options(self) -> Options:
        call_options = CallOptions(call_allowed=True, required_tool_name=self.selected_tool)
        return Options(call_options=call_options)


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

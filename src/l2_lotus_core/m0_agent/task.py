from __future__ import annotations
from queue import Queue


class Task:
    def __init__(self, is_work_task : bool = True, tool_call_allowed : bool = True):
        self._is_work_task : bool = is_work_task
        self._tool_call_allowed : bool = tool_call_allowed

    def is_dialogue_task(self) -> bool:
        return not self._is_work_task

    def is_work_task(self) -> bool:
        return self._is_work_task

    def get_tool_call_allowed(self) -> bool:
        return self._tool_call_allowed

    @classmethod
    def make_work_task(cls) -> Task:
        return cls(is_work_task=True)

    @classmethod
    def make_dialogue_task(cls) -> Task:
        return cls(is_work_task=False)


class TaskQueue(Queue):
    def __init__(self):
        super().__init__()
        self.queued_items : set = set()
        self.work_mode_enabled : bool = False

    def put(self, item : Task, block=True, timeout=None) -> None:
        super().put(item, block, timeout)
        self.queued_items.add(item)

    def get(self, block=True, timeout=None) -> Task:
        new_task = super().get(block, timeout)
        self.queued_items.remove(new_task)
        return new_task

    def work_task_present(self):
        return any(task.is_work_task() for task in self.queued_items)

    def dialogue_task_present(self):
        return any(task.is_dialogue_task() for task in self.queued_items)



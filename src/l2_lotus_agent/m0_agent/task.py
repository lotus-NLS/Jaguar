from __future__ import annotations
from queue import Queue
from typing import Optional


class Task:
    def __init__(self, is_mandate_task : bool = True, enforce_init_mandate : bool = False):
        self._is_work_task : bool = is_mandate_task
        self.requires_init_mandate : bool = enforce_init_mandate

    def is_dialogue_task(self) -> bool:
        return not self._is_work_task

    def is_mandate_task(self) -> bool:
        return self._is_work_task

    def requires_init_mandate(self) -> bool:
        return self.requires_init_mandate

    @classmethod
    def make_work_task(cls) -> Task:
        return cls(is_mandate_task=True)

    @classmethod
    def make_dialogue_task(cls, enforce_init_mandate : Optional[bool] = None) -> Task:
        if enforce_init_mandate is None:
            return cls(is_mandate_task=False)
        else:
            return cls(is_mandate_task=False,enforce_init_mandate=enforce_init_mandate)


class TaskQueue(Queue):
    def __init__(self):
        super().__init__()
        self.queued_items : set = set()
        self.work_mode_enabled : bool = False
        self._active_task : Optional[Task] = None

    def put(self, item : Task, block=True, timeout=None) -> None:
        super().put(item, block, timeout)
        self.queued_items.add(item)

    def get(self, block=True, timeout=None) -> Task:
        new_task = super().get(block, timeout)
        self.queued_items.remove(new_task)
        self._active_task = new_task
        return new_task

    def complete_active_task(self) -> None:
        self._active_task = None

    def view_active_task(self) -> Optional[Task]:
        return self._active_task

    def get_work_task_present(self) -> bool:
        return any(task.is_mandate_task() for task in self.queued_items)

    def get_dialogue_task_present(self) -> bool:
        return any(task.is_dialogue_task() for task in self.queued_items)



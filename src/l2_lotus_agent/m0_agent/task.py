from __future__ import annotations
from queue import Queue
from typing import Optional

from src.l3_lotus_core import Entry

# ---------------------------------------------------------

class Task:
    def __init__(self, is_mandate_task : bool = True, enforce_init_mandate : bool = False, entries_to_respond_to : Optional[list[Entry]] = None):
        self._is_work_task : bool = is_mandate_task
        self.requires_init_mandate : bool = enforce_init_mandate
        self._entries_to_process : list[Entry] = entries_to_respond_to if not entries_to_respond_to is None else []

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
    def make_dialogue_task(cls, enforce_init_mandate : bool = False, entries_to_process : Optional[list[Entry]] = None) -> Task:
        return cls(is_mandate_task=False,
                   enforce_init_mandate=enforce_init_mandate,
                   entries_to_respond_to=entries_to_process)

    def get_unread_as_str(self) -> str:
        unread_msg = ''
        for entry in self._entries_to_process:
            unread_msg += str(entry)

        return unread_msg

class TaskQueue(Queue):
    def __init__(self):
        super().__init__()
        self.queued_items : set = set()
        self.work_mode_enabled : bool = False
        self._active_task : Optional[Task] = None

    def put(self, item : Task, block=True, timeout=None):
        super().put(item, block, timeout)
        self.queued_items.add(item)

    def get(self, block=True, timeout=None) -> Task:
        new_task = super().get(block, timeout)
        self.queued_items.remove(new_task)
        self._active_task = new_task
        return new_task

    def complete_active_task(self):
        self._active_task = None

    def view_active_task(self) -> Optional[Task]:
        return self._active_task

    def get_work_task_present(self) -> bool:
        return any(task.is_mandate_task() for task in self.queued_items)

    def get_dialogue_task_present(self) -> bool:
        return any(task.is_dialogue_task() for task in self.queued_items)



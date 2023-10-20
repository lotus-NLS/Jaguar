from __future__ import annotations
from queue import Queue
from typing import Optional
from src.l3_lotus_core import Entry, DialogueRole

from src.l2_lotus_agent.m1_protocol import Mandate
# ---------------------------------------------------------

class Task:
    def __init__(self,
                 mandate : Optional[Mandate],
                 entries_to_respond_to : Optional[list[Entry]] = None,
                 required_funct_name : Optional[str] = None):

        self.mandate : Optional[Mandate] = mandate
        self.required_funct_name : Optional[str] = required_funct_name
        self._entries_to_process : list[Entry] = entries_to_respond_to if not entries_to_respond_to is None else []
        self.skip_feedback : bool = False if self.required_funct_name is None else True

    # ---------------------------------------------------------
    # get

    def get_entry(self) -> Entry:
        if self.is_mandate_task():
            task_entry = Entry(DialogueRole.system_role(), msg=self.mandate.get_msg())
        else:
            task_entry = Entry(DialogueRole.system_role(), msg=f'New user messages to respond to:\n{self.get_unread_as_str()}')

        return task_entry

    def is_dialogue_task(self) -> bool:
        return self.mandate is None

    def is_mandate_task(self) -> bool:
        return not self.is_dialogue_task()

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

    def put(self, item : Task, block=True, timeout=None):
        super().put(item, block, timeout)
        self.queued_items.add(item)

    def get(self, block=True, timeout=None) -> Task:
        new_task = super().get(block, timeout)
        self.queued_items.remove(new_task)
        return new_task

    def get_work_task_present(self) -> bool:
        return any(task.is_mandate_task() for task in self.queued_items)

    def get_dialogue_task_present(self) -> bool:
        return any(task.is_dialogue_task() for task in self.queued_items)



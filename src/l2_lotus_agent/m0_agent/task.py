from __future__ import annotations
from queue import Queue
from typing import Optional
from src.l3_lotus_core import Entry, DialogueRole

from src.l2_lotus_agent.m2_protocol import Mandate


# ---------------------------------------------------------

class Task:
    def __init__(self,
                 mandate : Optional[Mandate] = None,
                 enforce_init_mandate : bool = False,
                 entries_to_respond_to : Optional[list[Entry]] = None):

        self.mandate : Optional[Mandate] = mandate
        self.requires_mandate_init : bool = enforce_init_mandate
        self._entries_to_process : list[Entry] = entries_to_respond_to if not entries_to_respond_to is None else []


    @classmethod
    def make_work_task(cls, mandate : Mandate) -> Task:
        return cls(mandate)

    @classmethod
    def make_dialogue_task(cls, enforce_init_mandate : bool = False, entries_to_process : Optional[list[Entry]] = None) -> Task:
        return cls(enforce_init_mandate=enforce_init_mandate,
                   entries_to_respond_to=entries_to_process)

    # ---------------------------------------------------------
    # get

    def get_entry(self) -> Entry:
        if self.is_mandate_task():
            task_entry = Entry(DialogueRole.system_role(), msg=self.mandate.get_msg())
        else:
            task_entry = Entry(DialogueRole.user_role(), msg=f'Respond to unread messages:\n{self.get_unread_as_str()}')

        return task_entry

    def is_dialogue_task(self) -> bool:
        return self.mandate is None

    def is_mandate_task(self) -> bool:
        return not self.is_dialogue_task()

    def requires_init_mandate(self) -> bool:
        return self.requires_mandate_init

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



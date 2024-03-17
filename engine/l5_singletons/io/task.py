from __future__ import annotations

from abc import abstractmethod
from typing import Optional

from api import Entry
from hollarek.core.logging import Loggable
from .pipes import TextPipe


class TaskHandler(Loggable):
    @abstractmethod
    def handle(self, task : Task) -> TextPipe:
        pass


class Task:
    def __init__(self, new_entries : list[Entry] = None, required_tool_name : Optional[str] = None):
        self.new_entries : list[Entry] = new_entries if new_entries else []
        self.selected_tool : Optional[str] = required_tool_name
        self.skip_feedback : bool = False if self.selected_tool is None else True

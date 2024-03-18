from __future__ import annotations
from enum import Enum


class Role(Enum):
    TOOL = 'function'
    USER = 'user'
    AGENT = 'assistant'
    SYSTEM = 'system'

    def __str__(self):
        return self.value


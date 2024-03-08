from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Role(Enum):
    TOOL = 'function'
    USER = 'user'
    AGENT = 'assistant'
    SYSTEM = 'system'


@dataclass
class Speaker:
    role : Role
    name : Optional[str] = None

    @classmethod
    def get_system(cls, name : Optional[str] = None) -> Speaker:
        return cls(role = Role.SYSTEM, name=name)

    @classmethod
    def get_tool(cls, name : str = 'unnamed_tool') -> Speaker:
        return cls(role= Role.TOOL,name=name)

    @classmethod
    def get_user(cls, name : Optional[str] = None) -> Speaker:
        return cls(role= Role.USER, name=name)

    @classmethod
    def get_agent(cls, name : Optional[str] = None) -> Speaker:
        return cls(role= Role.AGENT, name=name)

    def __post_init__(self):
        if not self.name and self.role == Role.TOOL:
            raise ValueError('Tool must have a name')

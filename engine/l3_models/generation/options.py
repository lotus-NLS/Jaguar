from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.l5_singletons import Task


@dataclass
class ToolOptions:
    call_allowed: bool
    required_tool_name: Optional[str] = None

    @classmethod
    def no_call(cls):
        return cls(call_allowed=False)

    @classmethod
    def auto(cls):
        return cls(call_allowed=True)


    def __post_init__(self):
        if not self.call_allowed and self.required_tool_name:
            raise ValueError('Cannot require a tool call if the call is not allowed')


    def get_openai_syntax(self) -> object:
        if not self.call_allowed:
            return 'none'

        if self.required_tool_name is None:
            return 'auto'
        else:
            return {"type" : "function", "function" : {'name' : f'{self.required_tool_name}'}}


@dataclass
class Options:
    tool_options : ToolOptions = ToolOptions.auto()
    max_tokens : Optional[int] = None
    temp : float = 0.3

    @classmethod
    def from_task(cls, task : Task):
        return cls(tool_options=ToolOptions(call_allowed=True, required_tool_name=task.required_tool_name))

    def get_call_allowed(self):
        return self.tool_options.call_allowed

    @classmethod
    def text_only(cls, max_tokens : Optional[int] = None, temp : float = 0.3):
        return cls(tool_options=ToolOptions.no_call(), max_tokens=max_tokens, temp=temp)
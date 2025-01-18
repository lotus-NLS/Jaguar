from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CallOptions:
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
    call_options: CallOptions = field(default_factory=CallOptions.auto)
    max_tokens : Optional[int] = None

    def get_call_allowed(self) -> bool:
        return self.call_options.call_allowed

    @classmethod
    def text_only(cls, **kwargs):
        return cls(call_options=CallOptions.no_call(), **kwargs)

    @classmethod
    def require_call(cls, tool_name: Optional[str] = None, **kwargs):
        return cls(call_options=CallOptions(call_allowed=True, required_tool_name=tool_name), **kwargs)
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.l3_aos.tools import Tool


# -----------------------------------------------------------------

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

    @classmethod
    def require_call(cls, tool_name : str):
        return cls(call_allowed=True, required_tool_name=tool_name)

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
class InfConfig:
    required_tool : Optional[Tool] = None
    timeout : float = 10
    input_tokens_max: int = 2**15
    disable_call: bool = False
    output_tokens_max : Optional[int] = None
    debugging : bool = True

    def __post_init__(self):
        if not self.required_tool is None and self.disable_call:
            raise ValueError('Cannot disable call if a required tool is set')

        if self.disable_call:
            self.call_options: CallOptions = CallOptions.no_call()
        elif self.required_tool:
            self.call_options : CallOptions = CallOptions.require_call(tool_name=self.required_tool.get_name())
        else:
            self.call_options : CallOptions = CallOptions.auto()

    def get_call_allowed(self) -> bool:
        return self.call_options.call_allowed

    @classmethod
    def text_only(cls, max_output_tokens : Optional[int] = None):
        return cls(disable_call=True, output_tokens_max=max_output_tokens)

    @classmethod
    def single_tool(cls, tool : Tool):
        return cls(required_tool=tool)
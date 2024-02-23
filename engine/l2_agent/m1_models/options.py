from __future__ import annotations
from typing import Optional
# ---------------------------------------------------------


class ActionOptions:
    def __init__(self, funct_call_options : ToolOptions, max_tokens : Optional[int] = None, temperature : float = 0.3):
        self.funct_call_options : ToolOptions = funct_call_options
        self.max_tokens : int = max_tokens
        self.temperature : float = temperature


    def get_funct_call_allowed(self):
        return self.funct_call_options.call_allowed



class ToolOptions:
    @classmethod
    def no_call(cls):
        return cls(allowed=False)

    @classmethod
    def make_auto_option(cls):
        return cls(allowed=True)

    def __init__(self, allowed : bool = True, required_func : Optional[str] = None):
        self.call_allowed : bool = allowed
        self.required_funct_name : Optional[str] = required_func

    def get_openai_syntax(self) -> object:
        if not self.call_allowed:
            return 'none'

        if self.required_funct_name is None:
            return 'auto'
        else:
            return {"type" : "function", "function" : {'name' : f'{self.required_funct_name}'}}




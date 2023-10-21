from __future__ import annotations

from typing import Optional


class FunctCallOption:
    @classmethod
    def make_no_call_option(cls):
        return cls(call_allowed=False)

    @classmethod
    def make_auto_option(cls):
        return cls(call_allowed=True)

    def __init__(self, call_allowed : bool = True, required_funct_name : Optional[str] = None):
        self.call_allowed : bool = call_allowed
        self.required_funct_name : Optional[str] = required_funct_name

    def get_openai_syntax(self) -> object:
        if not self.call_allowed:
            return 'none'

        if self.required_funct_name is None:
            return 'auto'
        else:
            return {'name' : f'{self.required_funct_name}'}


class ActionOptions:
    def __init__(self, funct_call_options : FunctCallOption, max_tokens : Optional[int] = None, temperature : float = 0.3):
        self.funct_call_options : FunctCallOption = funct_call_options
        self.max_tokens : int = max_tokens
        self.temperature : float = temperature


    def get_funct_call_allowed(self):
        return self.funct_call_options.call_allowed

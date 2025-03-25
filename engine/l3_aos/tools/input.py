from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from json_repair import repair_json

from holytools.devtools import Argument


# ---------------------------------------------------

@dataclass
class ToolArg:
    name : str
    desc: str = ''
    dtype : type =  str
    is_optional: bool = False
    choices : Optional[list[str]] = None

    def __post_init__(self):
        self.input : Optional[str] = None

        if not self.dtype in [int, bool, str]:
            raise TypeError(f"Unsupported type '{self.dtype.__name__}' for argument '{self.name}'."
                            f"Only basic dtypes {(int, bool, str)} are supported")
        if self.dtype == bool:
            self.choices = ['0', '1']

    @classmethod
    def from_function_arg(cls, arg: Argument):
        choices = [choice.name for choice in arg.dtype] if issubclass(arg.dtype, Enum) else None
        desc = '' if not arg.has_default_val() else f'Default value if left unspecified is \"{arg.get_default_val()}\"'
        return cls(name=arg.name, dtype=arg.dtype, is_optional=arg.has_default_val(), desc=desc, choices=choices)

    # ---------------------------------------------------

    def get_value(self) -> Optional[int, bool, str]:
        val = self.input

        try:
            requires_conversion = self.dtype is int or self.dtype is bool
            if requires_conversion and not val is None:
                val = int(val)
                if self.dtype is bool:
                    val = bool(val)
        except ValueError:
            raise ValueError(f"Invalid input type for '{self.name}'. Expected a value of type {self.dtype.__name__}, got '{self.input}'")
        return val

    def is_set(self) -> bool:
        return not self.input is None

    def input_is_valid(self) -> bool:
        if self.choices is None:
            return True
        return self.input in self.choices

    # ---------------------------------------------------

    def get_json_doc(self) -> dict[str,str]:
        arg_doc = {
            'type': 'string',
            'description': f'{self.desc}'
        }

        if not self.choices is None:
            arg_doc['enum'] = self.choices
        return arg_doc


class ToolCall:
    def __init__(self, name : str = '', json_str : str = ''):
        self.name : str = name
        self.json_str : str = json_str

    @classmethod
    def from_dict(cls, attr_dict : dict) -> ToolCall:
        return cls(json_str=json.dumps(attr_dict))

    def update(self, other : ToolCall):
        self.name += other.name
        self.json_str += other.json_str

    def get_args_dict(self) -> dict:
        if len(self.json_str) == 0:
            raise ValueError('Empty json string')

        try:
            tool_args_dict = json.loads(s=self.json_str)
        except:
            json_str = repair_json(json_str=self.json_str)
            tool_args_dict = json.loads(s=json_str)
        return tool_args_dict

    def __str__(self):
        return f'{self.name}: {self.json_str}'


if __name__ == "__main__":
    ta = ToolArg(name='test', dtype=int, is_optional=True)
    testval = ta.get_value()
    print('done')

    bool(3)
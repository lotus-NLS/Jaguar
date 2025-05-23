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
            raise ValueError(f"Invalid input type for ToolArg '{self.name}'. Expected a value of type {self.dtype.__name__}, got '{self.input}'")
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


class ToolDoc(dict):
    @classmethod
    def from_info(cls, name : str, desc : str, args : list[ToolArg]) -> ToolDoc:
        function_doc = {
            'name': name,
            'description': desc,
            'parameters': {
                'type': 'object',
                'properties': {arg.name: arg.get_json_doc() for arg in args},
                'required': [arg.name for arg in args if not arg.is_optional]
            },
        }

        tool_doc = {
            'type': 'function',
            'function': function_doc
        }

        return cls(tool_doc)

    def __eq__(self, other):
        return self.get_view() == other.get_editor()

    def get_view(self) -> str:
        func_name = self.get_tool_name()
        quick_desc = self.get_desc()
        info_str = f'- {func_name}: {quick_desc}'
        arg_dict = self.get_parameters()
        for arg_name, arg_dict in arg_dict.items():
            conditional_optional = f' (optional) ' if not arg_name in self.get_required() else ''
            arg_str = f'  - {arg_name}{conditional_optional}: {arg_dict["description"]}'
            info_str += f'\n{arg_str}'

        return info_str

    def get_tool_name(self) -> str:
        return self['function']['name']

    def get_desc(self) -> str:
        return self['function']['description']

    def get_parameters(self) -> dict:
        return self['function']['parameters']['properties']

    def get_required(self) -> list[str]:
        return self['function']['parameters']['required']


class ToolCall:
    def __init__(self, name : str = '', args_json : str = ''):
        self.name : str = name
        self.args_json : str = args_json

    @classmethod
    def no_args(cls, name : str) -> ToolCall:
        return cls(name=name, args_json='{}')

    @classmethod
    def from_dict(cls, attr_dict : dict) -> ToolCall:
        return cls(args_json=json.dumps(attr_dict))

    def update(self, other : ToolCall):
        self.name += other.name
        self.args_json += other.args_json

    def get_args_dict(self) -> dict:
        if len(self.args_json) == 0:
            raise ValueError('Empty json string')

        try:
            tool_args_dict = json.loads(s=self.args_json)
        except:
            json_str = repair_json(json_str=self.args_json)
            tool_args_dict = json.loads(s=json_str)
        for k, v in tool_args_dict.items():
            if isinstance(v, int):
                v = str(v)
            if isinstance(v, bool):
                v = str(int(v))
            if not isinstance(v, str):
                raise ValueError(f'Invalid json string: {self.args_json}, includes non-string values')
            tool_args_dict[k] = v

        return tool_args_dict

    def __str__(self):
        return f'{self.name}: {self.args_json}'



if __name__ == "__main__":
    ta = ToolArg(name='test', dtype=int, is_optional=True)
    testval = ta.get_value()
    print('done')

    bool(3)
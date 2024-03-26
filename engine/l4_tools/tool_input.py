from __future__ import annotations
import json
from typing import Optional,Any
from json_repair import repair_json
from dataclasses import dataclass
from enum import Enum
from hollarek.devtools import Argument
# ---------------------------------------------------

@dataclass
class ToolArg:
    name : str
    desc: str = ''
    dtype : type =  str
    is_optional: bool = False
    choices : Optional[list[str]] = None

    def __post_init__(self):
        self.input : Optional[Any] = None
        if self.dtype == bool:
            self.choices = ['0', '1']

        if not self.is_supported(self.dtype):
            raise TypeError(f"Unsupported type '{self.dtype.__name__}' for argument '{self.name}'."
                            f"Supported types are {list(to_json_type.keys())}")

    @staticmethod
    def is_supported(python_type : type) -> bool:
        return not get_json_type(python_type) is None

    @classmethod
    def from_function_arg(cls, arg: Argument):
        choices = [choice.value for choice in arg.dtype] if issubclass(arg.dtype, Enum) else None
        desc = '' if not arg.has_default_val() else f'Default value if left unspecified is \"{arg.get_default_val()}\"'
        return cls(name=arg.name, dtype=arg.dtype, is_optional=arg.has_default_val(), desc=desc, choices=choices)

    # ---------------------------------------------------

    def get_arg_json_doc(self) -> dict[str,str]:
        arg_doc = {
            'type': get_json_type(python_type=str),
            'description': f'{self.desc}',
        }

        if not self.choices is None:
            arg_doc['enum'] = self.choices

        return arg_doc

    def get_value(self) -> Optional[Any]:
        val = self.input
        if val is None:
            return None
        try:
            if self.dtype is bool:
                 val = int(self.input)
            val = self.dtype(val)
        except ValueError:
            raise ValueError(f"Invalid input type for '{self.name}'. Expected a value of type {self.dtype.__name__}.")
        return val

    def input_is_valid(self) -> bool:
        if self.choices is None:
            return True
        return self.input in self.choices


    def is_set(self) -> bool:
        return not self.get_value() is None


class ToolCall:
    def __init__(self, name : str = '', json_str : str = '', index : int = 0):
        self.name : str = name if name else ''
        self.json_str : str = json_str if json_str else ''
        self.index : int = index

    def add(self, partial_call : ToolCall):
        self.name += partial_call.name
        self.json_str += partial_call.json_str


    def get_args_dict(self) -> dict:
        def as_string_decoder(pair: dict) -> dict:
            return {k: str(v) if v is not None else 'null' for k, v in pair.items()}

        def load(s) -> dict:
            return json.loads(s=s, object_hook=as_string_decoder)

        try:
            tool_args_dict = load(s=self.json_str)
        except:
            tool_args_dict = load(s=repair_json(json_str=self.json_str))
        return tool_args_dict

    @classmethod
    def from_args_dict(cls, args_dict : dict) -> ToolCall:
        json_str = json.dumps(args_dict)
        return cls(json_str=json_str)



class ToolCallMap(dict[int, ToolCall]):
    def add(self, new : ToolCallMap):
        for index, call in new.items():
            if not index in self:
                self[index] = call
            else:
                self[index].add(partial_call=call)

    def get_tool_calls(self) -> list[ToolCall]:
        return list(self.values())

    def print_info(self):
        print(f'\n-> Generated tool calls')
        for call in list(self.values()):
            print(f'tool name: {call.name}')
            print(call.get_args_dict())

    def is_empty(self) -> bool:
        return len(self) == 0


def get_json_type(python_type: type) -> Optional[str]:
    base_type = Enum if issubclass(python_type, Enum) else python_type
    json_type = to_json_type.get(base_type)
    return json_type

to_json_type  : dict[type, str] = {int: "number", float: "number", str: "string", bool: "boolean",Enum : "string"}
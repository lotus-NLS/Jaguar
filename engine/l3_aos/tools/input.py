from __future__ import annotations
import json
from typing import Optional,Any
from json_repair import repair_json
from dataclasses import dataclass
from enum import Enum
from holytools.devtools import Argument

to_json_type: dict[type, str] = {int: "number", float: "number", str: "string", bool: "boolean", Enum: "string"}

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

        if self.get_json_type(python_type=self.dtype) is None:
            raise TypeError(f"Unsupported type '{self.dtype.__name__}' for argument '{self.name}'."
                            f"Supported types are {list(to_json_type.keys())}")

    @classmethod
    def from_function_arg(cls, arg: Argument):
        choices = [choice.name for choice in arg.dtype] if issubclass(arg.dtype, Enum) else None
        desc = '' if not arg.has_default_val() else f'Default value if left unspecified is \"{arg.get_default_val()}\"'
        return cls(name=arg.name, dtype=arg.dtype, is_optional=arg.has_default_val(), desc=desc, choices=choices)

    # ---------------------------------------------------

    def get_value(self) -> Optional[Any]:
        val = self.input
        try:
            if self.dtype is bool:
                val = int(val)
            if issubclass(self.dtype, Enum):
                val =  self.dtype[val]
            val = self.dtype(val)
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
            'type': self.get_json_type(python_type=str),
            'description': f'{self.desc}'
        }

        if not self.choices is None:
            arg_doc['enum'] = self.choices
        return arg_doc

    @staticmethod
    def get_json_type(python_type: type) -> Optional[str]:
        base_type = Enum if issubclass(python_type, Enum) else python_type
        json_type = to_json_type.get(base_type)
        return json_type


class ToolCall:
    def __init__(self, name : str = '', json_str : str = ''):
        self.name : str = name if name else ''
        self.json_str : str = json_str

    def __iadd__(self, other : ToolCall):
        self.name += other.name
        self.json_str += other.json_str

    def get_args_dict(self) -> dict:
        if len(self.json_str) == 0:
            raise ValueError('Empty json string')

        try:
            tool_args_dict = self.load(s=self.json_str)
        except:
            tool_args_dict = self.load(s=repair_json(json_str=self.json_str))
        return tool_args_dict

    @classmethod
    def from_args_dict(cls, args_dict : dict) -> ToolCall:
        json_str = json.dumps(args_dict)
        return cls(json_str=json_str)

    @staticmethod
    def load(s : str) -> dict:
        def as_string_decoder(pair: dict) -> dict:
            return {k: str(v) if v is not None else 'null' for k, v in pair.items()}
        obj = json.loads(s=s, object_hook=as_string_decoder)

        if not isinstance(obj, dict):
            raise ValueError(f"Expected a dictionary, got {type(obj)}")

        return obj



from __future__ import annotations
import json
from typing import Optional,Any
from json_repair import repair_json
from hollarek.logging import debug
from hollarek.devtools import Argument
from dataclasses import dataclass
# ---------------------------------------------------

@dataclass
class ToolArg:
    name : str
    desc : str
    is_optional: bool
    dtype : type =  str
    choices : Optional[list[str]] = None
    input : Optional[str] = None

    def __post_init__(self):
        self.choices = self.choices if not self.dtype == bool else ['0', '1']
        if not self.dtype in get_supported_types():
            raise TypeError(f"Unsupported type '{self.dtype.__name__}' for argument '{self.name}'."
                            f"Supported types are {get_supported_types()}")

    @classmethod
    def from_function_arg(cls, arg: Argument):
        return cls(name=arg.name, dtype=arg.dtype, is_optional=arg.has_default_val(), desc='')


    def get_arg_json_doc(self) -> dict[str,str]:
        arg_doc = {
            'type': get_json_type(python_type=str),
            'description': f'{self.desc}',
        }

        if not self.choices is None:
            arg_doc['enum'] = self.choices

        return arg_doc


    def get_value(self) -> Optional[Any]:
        if self.input is None:
            return None
        try:
            val = self.dtype(self.input)
        except ValueError:
            raise ValueError(f"Invalid input type for '{self.name}'. Expected a value of type {self.dtype.__name__}.")
        return val


    def input_is_valid(self) -> bool:
        if self.choices is None:
            return True

        return self.input in self.choices


class ToolDoc(dict[str, Any]):
    @classmethod
    def from_info(cls, name : str, desc : str, args : list[ToolArg]) -> ToolDoc:
        required_arg_names = [arg.name for arg in args if not arg.is_optional]
        arg_docs = {arg.name: arg.get_arg_json_doc() for arg in args}
        function_doc = {
            'name': name,
            'description': desc,
            'parameters': {
                'type': 'object',
                'properties': arg_docs,
                'required': required_arg_names
            },
        }

        tool_doc = {
            'type': 'function',
            'function': function_doc
        }

        return cls(tool_doc)


    def get_is_valid_json(self) -> bool:
        try:
            json.dumps(self)
            return True
        except:
            return False


class ToolCall:
    def __init__(self, name : Optional[str] = None, json_str : Optional[str] = None, index : int  = 0):
        self.name : str  = name if not name is None else ''
        self.json_str : str = json_str if not json_str is None else ''
        self.index: int = index


    def add(self, partial_call : ToolCall):
        self.name += partial_call.name
        self.json_str += partial_call.json_str


    def get_args_dict(self):
        try:
            tool_args_dict = json.loads(s=self.json_str)
        except:
            tool_args_dict = json.loads(s=repair_json(json_str=self.json_str))
        return tool_args_dict


class CallMap(dict[int, ToolCall]):
    def add(self, new : CallMap):
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
            debug(call.get_args_dict())



def get_json_type(python_type : type) -> Optional[str]:
    json_type = python_to_json_type.get(python_type)
    return json_type

def get_supported_types() -> list[type]:
    return list(python_to_json_type.keys())

python_to_json_type : dict[type, str] = {
    int: "number",
    float: "number",
    str: "string",
    bool: "boolean",
    dict: "object"
}



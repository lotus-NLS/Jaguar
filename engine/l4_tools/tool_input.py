from __future__ import annotations
import json
from typing import Optional,Any
from json_repair import repair_json
from hollarek.devtools import Argument
from dataclasses import dataclass
# ---------------------------------------------------

@dataclass
class ToolArg:
    name : str
    desc: str = ''
    dtype : type =  str
    is_optional: bool = False
    choices : Optional[list[str]] = None
    input : Optional[str] = None

    def __post_init__(self):
        self.choices = self.choices if not self.dtype == bool else ['0', '1']
        self.to_json_type: dict[type, str] = {
            int: "number",
            float: "number",
            str: "string",
            bool: "boolean",
            dict: "object"}


        if not self.dtype in self.get_supported_types():
            raise TypeError(f"Unsupported type '{self.dtype.__name__}' for argument '{self.name}'."
                            f"Supported types are {self.get_supported_types()}")

    def get_json_type(self,python_type: type) -> Optional[str]:
        json_type = self.to_json_type.get(python_type)
        return json_type

    def get_supported_types(self) -> list[type]:
        return list(self.to_json_type.keys())

    @classmethod
    def from_function_arg(cls, arg: Argument):
        desc = '' if not arg.has_default_val() else f'Default value if left unspecified is \"{arg.get_default_val()}\"'
        return cls(name=arg.name, dtype=arg.dtype, is_optional=arg.has_default_val(), desc=desc)


    def get_arg_json_doc(self) -> dict[str,str]:
        arg_doc = {
            'type': self.get_json_type(python_type=str),
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

    def get_tool_name(self):
        return self['function']['name']

    def get_is_valid_json(self) -> bool:
        try:
            json.dumps(self)
            return True
        except:
            return False

    def as_str(self, pretty: bool = False) -> str:
        relevant_doc = self['function']
        indent = 4 if pretty else None
        return json.dumps(relevant_doc, indent=indent)


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


from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Callable, Dict, Any, Union
from pyutils import DevLogger

from engine.l2_agent.m1_models import MultiToolCall
# ---------------------------------------------------------


class ToolHandler:
    def __init__(self):
        self.tool_dict : dict[str,ToolInterface] = {}
        self.multi_tool_call : Optional[MultiToolCall] = None

    def reset_toolcall(self):
        self.multi_tool_call = MultiToolCall()

    def tool_call_requested(self) -> bool:
        return not len(self.multi_tool_call.get_as_list()) == 0

    def execute_multitool_calls(self):
        for tool_call in self.multi_tool_call.get_as_list():
            print(f'[Debug]: Agent requested tool usage with args {tool_call}')

            try:
                tool_call.try_parse_json()

            except:
                print(DevLogger.get_exception_msg(text=f'An occured while trying to parse tool json str: {tool_call.json_str}'))

            try:
                tool_name = tool_call.get_tool_name()
                tool_args_dict = tool_call.get_arguments()

                if tool_name in self.tool_dict:
                    self.tool_dict[tool_name].handle_call(args_dict=tool_args_dict)
            except:
                print(DevLogger.get_exception_msg(text=f'An error occured while trying handle tool call'))

    def get_all_tools(self) -> list[ToolInterface]:
        return list(self.tool_dict.values())

    def get_tool_doc(self, name : str) -> dict:
        return self.tool_dict[name].get_json_doc()

    def get_public_tool_docs(self) -> Optional[list[dict]]:
        return [tool.get_json_doc() for tool in self.tool_dict.values() if tool.is_public_tool]


class ToolInterface(ABC):
    def __init__(self):
        self.name: str = self.__class__.__name__
        self.desc: str = ''
        self.external_log: Callable = lambda *args, **kwargs: None
        self.arg_dict: dict[str, ToolArg] = {}
        self.is_public_tool: bool = True


    @abstractmethod
    def handle_call(self, args_dict: Dict[str, Any]):
        pass

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def get_json_doc(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def reset_args(self):
        pass


class ToolArg:
    def __init__(self, name : str, dtype : type, desc : str,
                 available_options : Optional[list[str]] = None,
                 is_optional : bool = False):
        self.name : str = name
        self.dtype : type = dtype
        self.description : str = desc
        self.available_options: Optional[list[str]] = available_options
        self.is_optional : bool = is_optional

        self.val : Optional = None


    def get_arg_json_doc(self) -> dict[str,str]:
        arg_doc = {
            'type': self.get_json_type(self.dtype),
            'description': f'{self.description}',
        }

        if not self.available_options is None:
            arg_doc['enum'] = self.available_options

        return arg_doc

    @staticmethod
    def get_json_type(python_type) -> Union[str,None]:
        # The 'array' type corresponding to dict and list, seem to break something on OpenAI end,
        # hence why I didn't include them; See logs (@ https://www.notion.so/pyWrite0-3-a53c1b16ef3646df9c141a144f8197a2)

        default_type = 'string'
        type_mapping = {
            int: "number",
            float: "number",
            str: "string",
            bool: "boolean",
            type(None): "null",
            dict: "object"
        }

        if python_type in type_mapping:
            json_type = type_mapping[python_type]
        else:
            json_type = default_type

        return json_type


    def value_is_valid(self) -> bool:
        if self.available_options is None:
            return True

        return self.val in self.available_options

from __future__ import annotations

import json
from typing import Any

from func_timeout import func_timeout, FunctionTimedOut
from abc import abstractmethod

from holytools.logging import LoggerFactory
from .output import MissingArgs, InvalidArgValue, ToolOutput, ProgressUpdate, ToolException
from .input import ToolCall, ToolArg

# ---------------------------------------------------------

class Tool:
    def __init__(self, call_timeout : float = 60):
        self.is_active : bool = True
        self.logger = LoggerFactory.get_logger(name=f'{self.__class__}')
        self.timeout : float = call_timeout

    # ---------------------------------------------------
    # call

    def handle(self, tool_call: ToolCall) -> ToolOutput:
        output = ToolOutput(tool_name=self.get_name(), call_args=tool_call.get_args_dict())
        output.update(msg=f'Starting \"{self.get_name()}\" with args {tool_call.get_args_dict()}', progress_type=ProgressUpdate.START)
        try:
            self._set_args(tool_call=tool_call)
            output.update(msg=f'Running tool \"{self.get_name()}\"', progress_type=ProgressUpdate.INFO)
            output.value = func_timeout(timeout=self.timeout, func=self.do)
            output.update(msg=f'Tool \"{self.get_name()}\" completed execution', progress_type=ProgressUpdate.FINISH)

        except ToolException as e:
            output.update(msg=f'{e.__class__.__name__}: {e}', progress_type=ProgressUpdate.FAILED)
        except FunctionTimedOut:
            output.update(msg=f'Timed out without completing after {self.timeout} seconds', progress_type=ProgressUpdate.FAILED)
        except Exception as e:
            output.update(msg=f'Encountered exception: {e}. Aborting ...', progress_type=ProgressUpdate.EXCEPTION)
        finally:
            output.update(msg=f'Tool call finished', progress_type=ProgressUpdate.FINISH)

        return output

    def _set_args(self, tool_call : ToolCall):
        for arg in self.get_args():
            arg.input = None

        args_dict = tool_call.get_args_dict()
        required_args = [arg for arg in self.get_args() if not arg.is_optional]
        missing_args = [arg.name for arg in required_args if not arg.name in args_dict]
        if missing_args:
            raise MissingArgs(f'Provided dictionary {args_dict} did not cover required args {missing_args}')

        specified_args = [arg for arg in self.get_args() if arg.name in args_dict]
        for arg in specified_args:
            arg.input = args_dict[arg.name]
            if not arg.input_is_valid():
                raise InvalidArgValue(f'Argument value \"{arg.input}\" is not in allowed choices \"{arg.choices}\" for argument \"{arg.name}\"')
        return specified_args


    @abstractmethod
    def do(self):
        pass

    # ---------------------------------------------------
    # Get

    def get_doc(self) -> ToolDoc:
        return ToolDoc.from_info(name=self.get_name(), desc=self.get_desc(), args=self.get_args())

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def get_desc(self) -> str:
        pass

    def get_args(self) -> list[ToolArg]:
        return [attr for attr in self.__dict__.values() if isinstance(attr, ToolArg)]


class ToolDoc(dict[str, Any]):
    @classmethod
    def from_info(cls, name : str, desc : str, args : list[ToolArg]) -> ToolDoc:
        required_arg_names = [arg.name for arg in args if not arg.is_optional]
        arg_docs = {arg.name: arg.get_json_doc() for arg in args}
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

    def get_tool_name(self) -> str:
        return self['function']['name']

    def as_str(self, pretty: bool = False) -> str:
        relevant_doc = self['function']
        indent = 4 if pretty else None
        return json.dumps(relevant_doc, indent=indent)

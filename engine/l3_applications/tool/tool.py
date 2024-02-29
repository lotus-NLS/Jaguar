import json
from typing import Any
from func_timeout import func_timeout, FunctionTimedOut
from abc import abstractmethod

from hollarek.dev import get_logger
from .output import MissingArgs, InvalidArgValue, ToolOutput, Update, WindowMap
from .input import ToolCall, ToolArg
# ---------------------------------------------------------

class Tool:
    def __init__(self, window_map : WindowMap, call_timeout : float = 60):
        self.window_map : WindowMap = window_map

        self.is_active : bool = True
        self.desc: str = ''
        self.logger = get_logger(name=self.get_name())
        self.timeout : float = call_timeout

    # ---------------------------------------------------
    # call

    def handle(self, tool_call: ToolCall) -> ToolOutput:
        report = ToolOutput(tool_name=self.get_name())
        report.update(msg=f'Starting {self.get_name()} with args {tool_call.get_args_dict()}', category=Update.START)
        try:
            self._set_args(tool_call=tool_call)
            report.update(msg=f'Running tool {self.get_name()}', category=Update.UPDATE)
            report.value = func_timeout(timeout=self.timeout, func=self.do)
            report.update(msg=f'Tool {self.get_name()} completed execution', category=Update.FINISH)

        except MissingArgs as e:
            report.update(msg=f'Missing Arguments: {e}', category=Update.FAILED)
        except FunctionTimedOut:
            report.update(msg=f'Timed out without completing after {self.timeout} seconds',category=Update.FAILED)
        except Exception as e:
            report.update(msg=f'Encounteredexception: {e}. Aborting ...',category=Update.EXCEPTION)
        finally:
            report.update(msg=f'Tool call finished', category=Update.FINISH)

        return report


    def _set_args(self, tool_call : ToolCall):
        for arg in self.get_args():
            arg.val = None

        args_dict = tool_call.get_args_dict()
        missing_required = not all(arg.name in args_dict for arg in self._get_required_args())
        if missing_required:
            raise MissingArgs(f'Provided dictionary {args_dict} did not cover all required tool arguments')

        specified_args = [arg for arg in self.get_args() if arg.name in args_dict]
        for arg in specified_args:
            arg.val = args_dict[arg.name]
            if not arg.value_is_valid():
                raise InvalidArgValue(f'Value {arg.val} is not in valid options {arg.choices} for argument {arg.name}')
        return specified_args


    @abstractmethod
    def do(self):
        pass

    # ---------------------------------------------------
    # Get

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__


    @classmethod
    @abstractmethod
    def get_application_name(cls):
        pass


    def get_json_doc(self) -> dict[str, Any]:
        required_arg_names = [arg.name for arg in self.get_args() if not arg.is_optional]
        arg_docs = {arg.name : arg.get_arg_json_doc() for arg in self.get_args()}

        if not self.desc:
            raise ValueError(f'\n[Error]: Tool {self.get_name()} has no description\nAborting ...')

        function_doc = {
            'name': f'{self.get_name()}',
            'description': f'{self.desc}',
            'parameters': {
                'type': 'object',
                'properties': {arg_docs},
                'required' : required_arg_names
            },
        }

        tool_doc = {
            'type' : 'function',
            'function' : function_doc
        }

        if not self.is_valid_json(tool_doc):
            raise ValueError(f'\n[Error]: Could not serialize object {tool_doc}\nAborting ...')

        return tool_doc


    def get_args_dict(self) -> dict[str, ToolArg]:
        return {arg.name : arg for arg in self.get_args()}


    def get_args(self) -> list[ToolArg]:
        return [val for name,val in self.__dict__ if isinstance(val, ToolArg)]


    def _get_required_args(self) -> list[ToolArg]:
        return [arg for arg in self.get_args() if not arg.is_optional]


    @staticmethod
    def is_valid_json(json_obj: dict) -> bool:
        try:
            json.dumps(json_obj)
            return True
        except:
            return False



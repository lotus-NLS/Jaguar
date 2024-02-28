import traceback
import json
from typing import Any
from func_timeout import func_timeout, FunctionTimedOut
from abc import abstractmethod

from hollarek.dev import get_logger
from .arg import ToolArg
from .toolcall import ToolCall, MissingArgs, InvalidArgValue
from .. import Phase


# ---------------------------------------------------------


class Tool:
    timout_in_sec = 60

    def __init__(self, has_context : bool = True):
        self.desc: str = ''
        self.logger = get_logger(name=self.get_name())
        self.___content_depr___ : str = ''

    # ---------------------------------------------------
    # call

    def handle(self, tool_call: ToolCall):
        self.log(f'Starting tool \"{self.get_name()}\" with args {self.get_args_dict()}', phase=Phase.START)
        try:
            self._set_args(tool_call=tool_call)
            self.log(f'Running tool {self.get_name()}', phase=Phase.START)
            func_timeout(timeout=Tool.timout_in_sec, func=self.do)
            self.log(f'Tool {self.get_name()} completed execution', phase=Phase.FINISH)

        except MissingArgs as e:
            self.log(f'Missing Arguments: {e}', phase=Phase.FAILED)
        except FunctionTimedOut:
            self.log(f'Tool timed out: {self.get_name()} timed out without completing after {Tool.timout_in_sec} seconds', phase=Phase.FINISH)
        except Exception as e:
            self.log(f'{self.get_name()} encountered an exception during execution: {e}. Aborting ...', phase=Phase.FAILED)
        finally:
            self.log(f'Tool call finished', Phase.FINISH)


    def _set_args(self, tool_call : ToolCall):
        for arg in self._get_args():
            arg.val = None

        args_dict = tool_call.get_args_dict()
        missing_required = not all(arg.name in args_dict for arg in self._get_required_args())
        if missing_required:
            raise MissingArgs(f'Provided dictionary {args_dict} did not cover all required tool arguments')

        specified_args = [arg for arg in self._get_args() if arg.name in args_dict]
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


    def get_json_doc(self) -> dict[str, Any]:
        required_arg_names = [arg.name for arg in self._get_args() if not arg.is_optional]
        arg_docs = {arg.name : arg.get_arg_json_doc() for arg in self._get_args()}

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
        return {arg.name : arg for arg in self._get_args()}


    def _get_args(self) -> list[ToolArg]:
        return [val for name,val in self.__dict__ if isinstance(val, ToolArg)]


    def _get_required_args(self) -> list[ToolArg]:
        return [arg for arg in self._get_args() if not arg.is_optional]


    @staticmethod
    def is_valid_json(json_obj: dict) -> bool:
        try:
            json.dumps(json_obj)
            return True
        except:
            return False


    def log(self, msg : str, phase : Phase, include_call_stack: bool = False):
        optiona_call_stack = f'\nCall stack: {traceback.format_exc()}' if include_call_stack else ''
        to_log = f'[{phase.value}]:{msg}{optiona_call_stack}'
        self.___content_depr___ += to_log
        self.logger.log(msg=to_log)

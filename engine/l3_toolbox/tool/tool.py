import traceback
import json
from typing import Any
from func_timeout import func_timeout, FunctionTimedOut
from abc import abstractmethod
from enum import Enum

from .tool_arg import ToolArg
from .tool_exceptions import MissingArgs, InvalidArgValue, ToolTimedOut
# ---------------------------------------------------------

class Phase(Enum):
    START = 'START'
    UPDATE = 'UPDATE'
    EXCEPTION = 'EXCEPTION'
    FAILED = 'FAILED'
    FINISH = 'FINISH'


class Tool:
    timout_in_sec = 60

    def __init__(self, is_public : bool = True):
        super().__init__()
        self.name: str = self.__class__.__name__
        self.desc: str = ''
        self.args_dict: dict[str, ToolArg] = {}
        self.is_public : bool = is_public


    def create_arg(self, tool_arg : ToolArg) -> ToolArg:
        self.args_dict[tool_arg.name] = tool_arg
        return tool_arg

    # ---------------------------------------------------
    # call

    def handle_call(self, args_dict: dict):
        self.log(f'Attempting to run {self.name} with args {self.args_dict}'

        try:
            self.set_args(args_dict=args_dict)
            self.log(f'Running tool {self.name}', phase=Phase.START)
            func_timeout(timeout=Tool.timout_in_sec, func=self.do)
            self.log(f'Tool {self.name} completed execution', phase=Phase.FINISH)

        except MissingArgs as e:
            self.log(f'Missing Arguments: {e}',phase=Phase.FAILED)
        except FunctionTimedOut:
            self.log(f'Tool timed out: {self.name} timed out without completing after {Tool.timout_in_sec} seconds', phase=Phase.FINISH)
        except Exception as e:
            self.log(f'{self.name} encountered an exception during execution: {e}. Aborting ...', phase=Phase.FAILED)

        finally:
            self.log(f'Tool call finished', Phase.FINISH)


    def set_args(self, args_dict : dict):
        for arg in self._get_args():
            arg.val = None

        missing_required = not all(arg.name in args_dict for arg in self._get_required_args())
        if missing_required:
            raise MissingArgs(f'Provided dictionary {args_dict} did not cover all required tool arguments')

        specified_args = [arg for arg in self._get_args() if arg.name in args_dict]
        for arg in specified_args:
            arg.val = args_dict[arg.name]
            if arg.value_is_valid():
                raise InvalidArgValue(f'Value {arg.val} is not in valid options {arg.choices} for argument {arg.name}')
        return specified_args


    @abstractmethod
    def do(self):
        pass

    # ---------------------------------------------------
    # Get

    def get_json_doc(self) -> dict[str, Any]:
        function_doc = {
            'name': f'{self.name}',
            'description': f'{self.desc}',
            'parameters': {
                'type': 'object',
                'properties': {}
            },
        }

        for arg in self._get_args():
            function_doc['parameters']['properties'][arg.name] = arg.get_arg_json_doc()

        function_doc['parameters']['required'] = [arg.name for arg in self._get_args() if not arg.is_optional]

        if not self.is_valid_json(function_doc):
            raise ValueError(f'\n[Error]: Could not serialize object {function_doc}\nAborting ...')

        tool_doc = {
            'type' : 'function',
            'function' : function_doc
        }

        return tool_doc


    def _get_args(self) -> list[ToolArg]:
        return list(self.args_dict.values())


    def _get_required_args(self) -> list[ToolArg]:
        return [arg for arg in self._get_args() if not arg.is_optional]


    @staticmethod
    def is_valid_json(json_obj: dict) -> bool:
        try:
            json.dumps(json_obj)
            return True
        except:
            return False

    @staticmethod
    def log(msg : str, phase : Phase, include_stacktrace: bool = False):
        print(f'[{phase.value}]:{msg}\nCall stack: {traceback.format_exc()}')

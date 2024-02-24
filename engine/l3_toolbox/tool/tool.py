import traceback
import json
from typing import Any
from func_timeout import func_timeout, FunctionTimedOut
from abc import abstractmethod
from enum import Enum
from engine.l3_toolbox.tool.tool_arg import ToolArg

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
    # Handle

    def handle_call(self, args_dict: dict):
        self.reset_args()
        self.log(f'Attempting to launch tool {self.name} with args: {args_dict}', phase=Phase.START)
        includes_required = all([arg.name for arg in self._get_required_args()])
        if not includes_required:
            self.log(f'Call failed since provided dictionary {args_dict} did not cover all required tool arguments',
                     phase=Phase.FAILED)
            return

        specified_args = [arg for arg in self._get_args() if arg.name in args_dict]
        for arg in specified_args:
            arg.val = args_dict[arg.name]
            if not arg.value_is_valid():
                self.log(f'Call failed since value {arg.val} is not in valid options {arg.choices} for argument {arg.name}',
                         phase=Phase.FAILED)
                return

        try:
            self.log(f'Tool {self.name} has been launched', phase=Phase.UPDATE)
            func_timeout(timeout=Tool.timout_in_sec, func=self.do)
            self.log(f'Tool {self.name} completed execution', phase=Phase.FINISH)

        except FunctionTimedOut:
            self.log(f'The tool {self.name} timed out without completing after {Tool.timout_in_sec} seconds. Aborting ...',
                     phase=Phase.FINISH)

        except Exception:
            self.log(f'The Tool {self.name} encountered the following error during execution:\n{traceback.format_exc()}\n'
                f'Aborting ...', phase=Phase.FINISH)

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


    def reset_args(self):
        for arg in self._get_args():
            arg.val = None

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
    def log(msg : str, phase : Phase):
        print(f'[{phase.value}]:{msg}')

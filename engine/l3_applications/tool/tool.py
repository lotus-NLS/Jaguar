import json
from typing import Any
from func_timeout import func_timeout, FunctionTimedOut
from abc import abstractmethod

from hollarek.logging import get_logger
from .output import MissingArgs, InvalidArgValue, ToolOutput, Progress, ToolException
from .input import ToolCall, ToolArg
# ---------------------------------------------------------

class Tool:
    def __init__(self, call_timeout : float = 60):
        self.is_active : bool = True
        self.logger = get_logger(name=self.get_name())
        self.timeout : float = call_timeout

    # ---------------------------------------------------
    # call

    def handle(self, tool_call: ToolCall) -> ToolOutput:
        output = ToolOutput(tool_name=self.get_name())
        output.update(msg=f'Starting \"{self.get_name()}\" with args {tool_call.get_args_dict()}', progress_type=Progress.START)
        try:
            self._set_args(tool_call=tool_call)
            output.update(msg=f'Running tool \"{self.get_name()}\"', progress_type=Progress.UPDATE)
            output.value = func_timeout(timeout=self.timeout, func=self.do)
            output.update(msg=f'Tool \"{self.get_name()}\" completed execution', progress_type=Progress.FINISH)

        except ToolException as e:
            output.update(msg=f'{e.__class__.__name__}: {e}', progress_type=Progress.FAILED)
        except FunctionTimedOut:
            output.update(msg=f'Timed out without completing after {self.timeout} seconds', progress_type=Progress.FAILED)
        except Exception as e:
            output.update(msg=f'Encounter edexception: {e}. Aborting ...', progress_type=Progress.EXCEPTION)
        finally:
            output.update(msg=f'Tool call finished', progress_type=Progress.FINISH)

        return output


    def _set_args(self, tool_call : ToolCall):
        for arg in self.get_args():
            arg.val = None

        args_dict = tool_call.get_args_dict()
        missing_args = [arg.name for arg in self._get_required_args() if not arg.name in args_dict]
        if missing_args:
            raise MissingArgs(f'Provided dictionary {args_dict} did not cover required args {missing_args}')

        specified_args = [arg for arg in self.get_args() if arg.name in args_dict]
        for arg in specified_args:
            arg.val = args_dict[arg.name]
            if not arg.value_is_valid():
                raise InvalidArgValue(f'Argument value \"{arg.val}\" is not in allowed choices \"{arg.choices}\" for argument \"{arg.name}\"')
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
    def get_desc(cls) -> str:
        pass


    def get_json_doc(self, application_name : str) -> dict[str, Any]:
        required_arg_names = [arg.name for arg in self.get_args() if not arg.is_optional]
        arg_docs = {arg.name : arg.get_arg_json_doc() for arg in self.get_args()}

        if not self.get_desc():
            raise ValueError(f'\n[Error]: Tool {self.get_name()} has no description\nAborting ...')

        function_doc = {
            'name': f'{application_name}_{self.get_name()}',
            'description': f'{self.get_desc()}; Application: {application_name}',
            'parameters': {
                'type': 'object',
                'properties': arg_docs,
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
        return [val for name,val in self.__dict__.items() if isinstance(val, ToolArg)]


    def _get_required_args(self) -> list[ToolArg]:
        return [arg for arg in self.get_args() if not arg.is_optional]


    @staticmethod
    def is_valid_json(json_obj: dict) -> bool:
        try:
            json.dumps(json_obj)
            return True
        except:
            return False



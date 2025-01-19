from __future__ import annotations

from abc import abstractmethod

from func_timeout import func_timeout, FunctionTimedOut

from holytools.logging import LoggerFactory
from .input import ToolCall, ToolArg
from .output import MissingArgs, InvalidArgValue, ToolOutput, ProgressUpdate, ToolException

# ---------------------------------------------------------

class Tool:
    def __init__(self, call_timeout : float = 60):
        self.is_active : bool = True
        self.logger = LoggerFactory.get_logger(name=f'{self.__class__}')
        self.timeout : float = call_timeout

    # ---------------------------------------------------
    # call

    def execute(self, tool_call: ToolCall) -> ToolOutput:
        output = ToolOutput(tool_name=self.get_name(), call_args=tool_call.get_args_dict())
        output.update(msg=f'Starting \"{self.get_name()}\" with args {tool_call.get_args_dict()}', progress_type=ProgressUpdate.START)
        try:
            self._set_args(tool_call=tool_call)
            output.update(msg=f'Running tool \"{self.get_name()}\"', progress_type=ProgressUpdate.INFO)
            output.value = func_timeout(timeout=self.timeout, func=self.do)
            output.update(msg=f'Tool \"{self.get_name()}\" completed execution sucessfully', progress_type=ProgressUpdate.INFO)

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

    @abstractmethod
    def get_desc(self) -> str:
        pass

    @abstractmethod
    def get_args(self) -> list[ToolArg]:
        pass

    # ---------------------------------------------------
    # Get

    def get_doc(self) -> ToolDoc:
        return ToolDoc.from_info(name=self.get_name(), desc=self.get_desc(), args=self.get_args())

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__




class ToolDoc(dict):
    @classmethod
    def from_info(cls, name : str, desc : str, args : list[ToolArg]) -> ToolDoc:
        function_doc = {
            'name': name,
            'description': desc,
            'parameters': {
                'type': 'object',
                'properties': {arg.name: arg.get_json_doc() for arg in args},
                'required': [arg.name for arg in args if not arg.is_optional]
            },
        }

        tool_doc = {
            'type': 'function',
            'function': function_doc
        }

        return cls(tool_doc)

    def __eq__(self, other):
        return self.get_view() == other.get_view()

    def get_view(self) -> str:
        func_name = self._get_tool_name()
        quick_desc = f'{self._get_desc()[100]}...' if len(self._get_desc()) > 100 else self._get_desc()
        info_str = f'- {func_name}: {quick_desc}'
        arg_dict = self._get_parameters()
        for arg_name, arg_dict in arg_dict.items():
            conditional_optional = f' (optional) ' if not arg_name in self._get_required() else ''
            arg_str = f'  - {arg_name}{conditional_optional}: {arg_dict["description"]}'
            info_str += f'\n{arg_str}'

        return info_str

    def _get_tool_name(self) -> str:
        return self['function']['name']

    def _get_desc(self) -> str:
        return self['function']['description']

    def _get_parameters(self) -> dict:
        return self['function']['parameters']['properties']

    def _get_required(self) -> list[str]:
        return self['function']['parameters']['required']

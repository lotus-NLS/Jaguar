from func_timeout import func_timeout, FunctionTimedOut
from abc import abstractmethod

from hollarek.core.logging import get_logger
from .tool_output import MissingArgs, InvalidArgValue, ToolOutput, Progress, ToolException
from .tool_input import ToolCall, ToolArg, ToolDoc
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
            output.update(msg=f'Encountered exception: {e}. Aborting ...', progress_type=Progress.EXCEPTION)
        finally:
            output.update(msg=f'Tool call finished', progress_type=Progress.FINISH)

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
        doc = ToolDoc.from_info(name=self.get_name(), desc=self.get_desc(), args=self.get_args())
        if not doc.get_is_valid_json():
            raise ValueError(f'\n[Error]: Tool {self.get_name()} has invalid json doc\nAborting ...')

        return doc

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    def get_desc(self) -> str:
        pass

    def get_args(self) -> list[ToolArg]:
        return [attr for attr in self.__dict__.values() if isinstance(attr, ToolArg)]
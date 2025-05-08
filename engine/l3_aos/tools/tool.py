from __future__ import annotations

import json
from abc import abstractmethod
from logging import Logger
from typing import Callable, Optional

from func_timeout import func_timeout, FunctionTimedOut

from holytools.devtools import ModuleInspector
from holytools.logging import LoggerFactory
from .input import ToolArg, ToolDoc, ToolCall
from .output import MissingArgs, InvalidArgValue, ToolOutput, ToolException


# ---------------------------------------------------------

class Tool:
    def __init__(self, call_timeout : float = 60):
        self.is_active : bool = True
        self.logger : Logger = LoggerFactory.get_logger(name=f'{self.__class__}')
        self.timeout : float = call_timeout
        self.prehook : Callable  = lambda *args, **kwargs : None

    # ---------------------------------------------------
    # call

    def add_prehook(self, pre_hook : Callable):
        args = ModuleInspector.get_args(pre_hook, exclude_self=True)
        non_default_args = [arg for arg in args if not arg.has_default_val()]
        if len(non_default_args) > 0:
            raise ValueError(f'Hook function \"{pre_hook.__name__}\" must not have any non-default arguments')
        self.prehook = pre_hook

    def execute(self, args_dict : dict) -> ToolOutput:
        output = ToolOutput(tool_name=self.get_name(), call_args=args_dict)
        output.start(msg=f'Starting \"{self.get_name()}\" with args {args_dict}')
        try:
            self._set_args(args_dict=args_dict)
            self.prehook()
            output.info(msg=f'Running tool \"{self.get_name()}\"')
            output.value = func_timeout(timeout=self.timeout, func=self._do)
            output.info(msg=f'Tool \"{self.get_name()}\" completed execution sucessfully')

        except ToolException as e:
            output.fail(msg=f'{e.__class__.__name__}: {e}')
        except FunctionTimedOut:
            output.fail(msg=f'Timed out without completing after {self.timeout} seconds')
        except Exception as e:
            output.error(msg=f'Encountered exception: {e}. Aborting ...')

        output.finish(msg=f'Tool call finished')

        return output

    def _set_args(self, args_dict : dict):
        for arg in self.get_args():
            arg.input = None

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
    def _do(self):
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

    def get_toolcall(self, args_dict : Optional[dict] = None) -> ToolCall:
        tc = ToolCall.no_args(name=self.get_name())
        if args_dict:
            tc.args_json = json.dumps(args_dict)
        return tc


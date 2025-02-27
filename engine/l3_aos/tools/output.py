from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any

from holytools.logging import LoggerFactory

tool_output_logger = LoggerFactory.get_logger(name=__name__)

# --------------------------------------------------

@dataclass
class ToolOutput:
    tool_name : str
    value : Optional[Any] = None
    call_args: Optional[dict] = None

    def __post_init__(self):
        super().__init__()
        self.progress_msgs : list[ProgressMsg] = []

    @classmethod
    def failed(cls, reason : str):
        output = cls(tool_name='None')
        output.update(msg=f'Failed: {reason}', progress_type=ProgressUpdate.FAILED)
        return output

    @classmethod
    def exception(cls, name : str, reason : Optional[BaseException] = None):
        output = cls(tool_name=name)
        conditional_reason = f': {reason}' if reason else ''
        output.update(msg=f'Tool{name} failed{conditional_reason}', progress_type=ProgressUpdate.EXCEPTION)
        return output

    def info(self, msg : str):
        self.update(msg=msg, progress_type=ProgressUpdate.INFO)

    def update(self, msg : str, progress_type : ProgressUpdate):
        progress_msg = ProgressMsg(progress_type=progress_type, content=msg)
        self.progress_msgs.append(progress_msg)
        tool_output_logger.info(str(progress_msg))

    def error(self, reason : str):
        self.update(msg=reason, progress_type=ProgressUpdate.EXCEPTION)

    def fail(self, reason : str):
        self.update(msg=reason, progress_type=ProgressUpdate.FAILED)

    # -----------------------------------------------------------

    def get_exit_status(self) -> ExitStatus:
        for progress in self.progress_msgs:
            if progress.progress_type == ProgressUpdate.EXCEPTION:
                return ExitStatus.EXCEPTION
            if progress.progress_type in [ProgressUpdate.FAILED]:
                return ExitStatus.FAILED
        return ExitStatus.SUCCESS

    def get_report(self) -> str:
        exit_status = self.get_exit_status()
        log_msg = (f'Tool \"{self.tool_name}\" finished execution with status:'
                   f' {exit_status.value}')
        if not exit_status == ExitStatus.SUCCESS:
            log_msg += f'; failure/exception reason: {self.get_error_msgs()}'
        log_msg += f'; Call arguments were {self.call_args}'
        return log_msg

    def get_error_msgs(self) -> list[str]:
        return [progress.content for progress in self.progress_msgs if progress.progress_type in [ProgressUpdate.EXCEPTION, ProgressUpdate.FAILED]]



class ProgressUpdate(Enum):
    START = 'START'
    INFO = 'INFO'
    EXCEPTION = 'EXCEPTION'
    FAILED = 'FAILED'
    FINISH = 'FINISH'


class ExitStatus(Enum):
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    EXCEPTION = 'EXCEPTION'

@dataclass
class ProgressMsg:
    progress_type : ProgressUpdate
    content : str

    def __str__(self):
        return f'[{self.progress_type.value}]: {self.content}'


class ToolException(Exception):
    pass

class MissingArgs(ToolException):
    pass

class InvalidArgValue(ToolException):
    pass


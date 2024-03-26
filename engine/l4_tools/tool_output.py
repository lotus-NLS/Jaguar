from __future__ import annotations

from api import Entry
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Any
from hollarek.core.logging import Loggable, LogLevel
# ---------------------------------------------------

class Progress(Enum):
    START = 'START'
    UPDATE = 'UPDATE'
    EXCEPTION = 'EXCEPTION'
    FAILED = 'FAILED'
    FINISH = 'FINISH'


class ExitStatus(Enum):
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    EXCEPTION = 'EXCEPTION'


@dataclass
class ProgressMsg:
    progress_type : Progress
    content : str

    def __str__(self):
        return f'[{self.progress_type.value}]: {self.content}'

@dataclass
class ToolOutput(Loggable):
    tool_name : str
    value : Optional[Any] = None
    progress: list[ProgressMsg] = field(default_factory=list)
    exit_status : ExitStatus = ExitStatus.SUCCESS

    def __post_init__(self):
        super().__init__()

    def get_report(self) -> str:
        log_msg = f'\"{self.tool_name}\" ran with exit status : \"{self.exit_status.value}\"'
        if not self.exit_status == ExitStatus.SUCCESS:
            log_msg += f'; failure/exception reason: {self.get_error_msgs()}'
        return log_msg


    def get_error_msgs(self) -> list[str]:
        return [progress.content for progress in self.progress if progress.progress_type in [Progress.EXCEPTION, Progress.FAILED]]


    def update(self, msg : str, progress_type : Progress):
        if progress_type == Progress.EXCEPTION:
            self.exit_status = ExitStatus.EXCEPTION
        if progress_type == Progress.FAILED:
            self.exit_status = ExitStatus.FAILED
        progress_msg = ProgressMsg(progress_type=progress_type, content=msg)
        self.progress.append(progress_msg)
        self.log(str(progress_msg), level=LogLevel.INFO)


    def as_entry(self) -> Entry:
        return Entry.as_tool(msg=self.get_report(), name =self.tool_name)

    @classmethod
    def not_found(cls, name : str):
        output = cls(tool_name='None')
        output.update(msg=f'Tool \"{name}\" not found', progress_type=Progress.FAILED)
        return output

    @classmethod
    def failed(cls, name : str, reason : Optional[BaseException] = None):
        output = cls(tool_name=name)
        conditional_reason = f': {reason}' if reason else ''
        output.update(msg=f'Tool{name} failed{conditional_reason}', progress_type=Progress.FAILED)
        return output

class ToolException(Exception):
    pass


class MissingArgs(ToolException):
    pass


class InvalidArgValue(ToolException):
    pass


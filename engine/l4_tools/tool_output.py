from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Any
from hollarek.logging import Loggable, LogLevel
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
    msg : str


@dataclass
class ToolOutput(Loggable):
    tool_name : str
    value : Optional[Any] = None
    progress: list[ProgressMsg] = field(default_factory=list)
    exit_status : ExitStatus = ExitStatus.SUCCESS

    def __post_init__(self):
        super().__init__()

    def get_report(self) -> str:
        log_msg = f'Report on tool \"{self.tool_name}\":\n'
        log_msg += f'Exit status: {self.exit_status.value}'

        if not ExitStatus == ExitStatus.SUCCESS:
            log_msg += f'; Reason: {self.get_error_msgs()}'
        return log_msg


    def get_error_msgs(self) -> list[str]:
        return [progress.msg for progress in self.progress if progress.progress_type in [Progress.EXCEPTION, Progress.FAILED]]


    def update(self, msg : str, progress_type : Progress):
        if progress_type == Progress.EXCEPTION:
            self.exit_status = ExitStatus.EXCEPTION
        if progress_type == Progress.FAILED:
            self.exit_status = ExitStatus.FAILED
        self.progress.append(ProgressMsg(progress_type=progress_type, msg=msg))
        self.log(f'[{progress_type.value}]: {msg}', level=LogLevel.INFO)


class ToolException(Exception):
    pass


class MissingArgs(ToolException):
    pass


class InvalidArgValue(ToolException):
    pass


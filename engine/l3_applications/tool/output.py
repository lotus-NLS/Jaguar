from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from abc import abstractmethod


from hollarek.dev.log import Loggable, LogLevel
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
    EXCPETION = 'EXCEPTION'


@dataclass
class ProgressMsg:
    update_type : Progress
    msg : str


class Window:
    def __init__(self, name : str):
        self.name : str = name
        self.content : str = ''

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_context(self) -> str:
        pass


class WindowMap(dict[int, Window]):
    pass


@dataclass
class ToolOutput(Loggable):
    tool_name : str
    window : Optional[Window] = None
    progress: list[ProgressMsg] = field(default_factory=list)
    exit_status : ExitStatus = ExitStatus.SUCCESS

    def get_report(self) -> str:
        log_msg = f'Report on tool {self.tool_name}:\n'
        log_msg += f'Exit status: {self.exit_status.value}'

        if not ExitStatus == ExitStatus.SUCCESS:
            log_msg += f'; Reason: {self.get_error_msgs()}'
        return log_msg


    def get_error_msgs(self) -> list[str]:
        return [update.msg for update in self.progress if update.update_type in [Progress.EXCEPTION, Progress.FAILED]]


    def update(self, msg : str, category : Progress):
        if category == Progress.EXCEPTION:
            self.exit_status = ExitStatus.EXCPETION
        if category == Progress.FAILED:
            self.exit_status = ExitStatus.FAILED
        self.progress.append(ProgressMsg(update_type=category, msg=msg))
        self.cls_log(f'[{category.value}]: {msg}', level=LogLevel.INFO)


class ToolException(Exception):
    pass


class MissingArgs(ToolException):
    pass


class InvalidArgValue(ToolException):
    pass




from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

from hollarek.dev.log import Loggable, LogLevel

# ---------------------------------------------------

class Update(Enum):
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
    update_type : Update
    msg : str


@dataclass
class ToolReport(Loggable):
    tool_name : str
    result : Optional[str] = None
    progress: list[ProgressMsg] = field(default_factory=list)
    exit_status : ExitStatus = ExitStatus.SUCCESS


    def as_msg(self) -> str:
        log_msg = f'Report on tool {self.tool_name}:\n'
        log_msg += f'Exit status: {self.exit_status.value}'

        if not ExitStatus == ExitStatus.SUCCESS:
            log_msg += f'; Reason: {self.get_error_msgs()}'
        else:
            log_msg += f'The following content was retrieved:\n\n{self.result}'
        return log_msg


    def get_error_msgs(self) -> list[str]:
        return [update.msg for update in self.progress if update.update_type in [Update.EXCEPTION, Update.FAILED]]


    def update(self, msg : str, category : Update):
        if category == Update.EXCEPTION:
            self.exit_status = ExitStatus.EXCPETION
        if category == Update.FAILED:
            self.exit_status = ExitStatus.FAILED
        self.progress.append(ProgressMsg(update_type=category, msg=msg))
        self.cls_log(f'[{category.value}]: {msg}', level=LogLevel.INFO)


class ToolException(Exception):
    pass


class MissingArgs(ToolException):
    pass


class InvalidArgValue(ToolException):
    pass




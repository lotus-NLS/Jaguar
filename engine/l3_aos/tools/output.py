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
        self.progress_msgs : list[ProgressUpdate] = []

    @classmethod
    def failed(cls, reason : str):
        output = cls(tool_name='None')
        output.fail(msg=f'Failed: {reason}')
        return output

    @classmethod
    def exception(cls, name : str, reason : Optional[BaseException] = None):
        output = cls(tool_name=name)
        conditional_reason = f': {reason}' if reason else ''
        output.error(msg=f'Tool{name} failed{conditional_reason}')
        return output

    def start(self, msg : str):
        self.log_update(ProgressUpdate.start(content=msg))

    def info(self, msg : str):
        self.log_update(ProgressUpdate.info(content=msg))

    def error(self, msg : str):
        self.log_update(ProgressUpdate.exception(content=msg))

    def fail(self, msg : str):
        self.log_update(ProgressUpdate.failed(content=msg))

    def finish(self, msg : str):
        self.log_update(ProgressUpdate.finish(content=msg))

    def log_update(self, update : ProgressUpdate):
        self.progress_msgs.append(update)
        tool_output_logger.info(str(update))

    # -----------------------------------------------------------

    def get_exit_status(self) -> ExitStatus:
        EXCEPTION = ProgressUpdate.exception(content='')
        FAILED = ProgressUpdate.failed(content='')

        for progress in self.progress_msgs:
            if progress.update_type == EXCEPTION.update_type:
                return ExitStatus.EXCEPTION
            if progress.update_type in [FAILED.update_type]:
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
        FAILED = ProgressUpdate.failed(content='')
        EXCEPTION = ProgressUpdate.exception(content='')

        return [progress.content for progress in self.progress_msgs if progress.update_type in [FAILED.update_type, EXCEPTION.update_type]]


class ExitStatus(Enum):
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    EXCEPTION = 'EXCEPTION'


@dataclass
class ProgressUpdate:
    update_type : str
    content : str

    @classmethod
    def start(cls, content : str) -> ProgressUpdate:
        return cls(update_type='START', content=content)

    @classmethod
    def info(cls, content : str) -> ProgressUpdate:
        return cls(update_type='INFO', content=content)

    @classmethod
    def exception(cls, content : str) -> ProgressUpdate:
        return cls(update_type='EXCEPTION', content=content)

    @classmethod
    def failed(cls, content : str) -> ProgressUpdate:
        return cls(update_type='FAILED', content=content)

    @classmethod
    def finish(cls, content : str) -> ProgressUpdate:
        return cls(update_type='FINISH', content=content)

    def __str__(self):
        return f'[{self.update_type}]: {self.content}'


class ToolException(Exception):
    pass

class MissingArgs(ToolException):
    pass

class InvalidArgValue(ToolException):
    pass


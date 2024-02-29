from __future__ import annotations
from enum import Enum


# ---------------------------------------------------


class ToolReport:
    pass

class ToolException(Exception):
    pass


class MissingArgs(ToolException):
    pass


class InvalidArgValue(ToolException):
    pass


class Phase(Enum):
    START = 'START'
    UPDATE = 'UPDATE'
    EXCEPTION = 'EXCEPTION'
    FAILED = 'FAILED'
    FINISH = 'FINISH'

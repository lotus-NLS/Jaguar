from __future__ import annotations
import json
from enum import Enum
from typing import Optional
from json_repair import repair_json

# ---------------------------------------------------


class ToolCall:
    def __init__(self, name : Optional[str], json_str : Optional[str], index : int  = 0):
        self.index : int  = index
        self.name : str  = name if not name is None else ''
        self.json_str : str = json_str if not json_str is None else ''


    def update(self, partial_call : ToolCall):
        self.name += partial_call.name
        self.json_str += partial_call.json_str


    def get_args_dict(self):
        try:
            tool_args_dict = json.loads(s=self.json_str)
        except:
            tool_args_dict = json.loads(s=repair_json(json_str=self.json_str))
        return tool_args_dict


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

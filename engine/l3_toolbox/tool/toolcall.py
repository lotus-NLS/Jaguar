from __future__ import annotations

import json
import logging
from typing import Optional, Union

from json_repair import repair_json


class SingleToolCall:
    def __init__(self, name : Optional[str], json_str : Optional[str], index : int):
        self.index : int  = index
        self.name : str  = name if not name is None else ''
        self.json_str : str = json_str if not json_str is None else ''
        self._arguments : Optional[dict] = None
        self.is_empty = True


    def update(self, partial_tool_call : SingleToolCall):
        self.is_empty = False
        self.name += partial_tool_call.name
        self.json_str += partial_tool_call.json_str



    def try_parse_json(self):
        json_str = self.json_str

        try:
            tool_args_dict = json.loads(s=json_str)
        except:
            logging.error(f'Given json string {json_str} is invalid. Attempting to salvage ...')
            tool_args_dict = json.loads(s=repair_json(json_str=json_str))

        self._arguments = tool_args_dict

    # ---------------------------------------------------
    # Actions

    def __str__(self):
        try:
            the_str = str(self.json_str)
        except:
            the_str = ''
        return the_str

    def get_tool_name(self) -> str:
        return self.name

    def get_arguments(self) -> dict:
        return self._arguments


class MultiToolCall:
    def __init__(self):
        self.tool_calls : dict[int, SingleToolCall] = {}


    def update(self, tool_call : Union[SingleToolCall, MultiToolCall]):
        if isinstance(tool_call, SingleToolCall):
            index = tool_call.index
            if self.tool_calls.get(index) is None:
                self.tool_calls[index] = tool_call
            else:
                self.tool_calls[index].update(partial_tool_call=tool_call)
        elif isinstance(tool_call, MultiToolCall):
            for tool_call in tool_call.get_as_list():
                self.update(tool_call=tool_call)

    def get_as_list(self):
        return self.tool_calls.values()

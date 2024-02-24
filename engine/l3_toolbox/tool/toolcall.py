from __future__ import annotations

import json
from typing import Optional, Union
from json_repair import repair_json

# ---------------------------------------------------


class ToolCall:
    def __init__(self, name : Optional[str], json_str : Optional[str], index : int  = 0):
        self.index : int  = index
        self.name : str  = name if not name is None else ''
        self.json_str : str = json_str if not json_str is None else ''

        self.is_empty = True
        self._arguments : Optional[dict] = None


    def update(self, partial_tool_call : ToolCall):
        self.is_empty = False
        self.name += partial_tool_call.name
        self.json_str += partial_tool_call.json_str


    def get_args_dict(self):
        try:
            tool_args_dict = json.loads(s=self.json_str)
        except:
            tool_args_dict = json.loads(s=repair_json(json_str=self.json_str))
        return tool_args_dict




class MultiToolCall:
    def __init__(self):
        self.tool_calls : dict[int, ToolCall] = {}


    def update(self, tool_call : Union[ToolCall, MultiToolCall]):
        if isinstance(tool_call, ToolCall):
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

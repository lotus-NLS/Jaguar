from __future__ import annotations
from typing import Optional
from engine.l3_application import Tool, ToolCall
# ---------------------------------------------------------


class ToolHandler:
    def __init__(self):
        self.tool_dict : dict[str,Tool] = {}
        self.tool_calls : list[ToolCall] = []


    def handle_calls(self):
        for tool_call in self.tool_calls:
            try:
                tool = self.tool_dict[tool_call.name]
                tool.handle(tool_call=tool_call)
            except:
                self.log(f'No tool found with name {tool_call.name}')
        self.reset_calls()


    def reset_calls(self):
        self.tool_calls = []


    def update(self, partial_calls : list[ToolCall]):
        pass

        # if isinstance(tool_call, ToolCall):
        #     index = tool_call.index
        #     if self.tool_calls.get(index) is None:
        #         self.tool_calls[index] = tool_call
        #     else:
        #         self.tool_calls[index].update(partial_call=tool_call)
        #
        #
        # elif isinstance(tool_call, MultiToolCall):
        #     for tool_call in tool_call.get_as_list():
        #         self.update(tool_call=tool_call)

    def get_tool_call_requested(self) -> bool:
        return not len(self.tool_calls) == 0


    def get_tool_doc(self, name : str) -> Optional[dict]:
        tool = self.tool_dict.get(name)
        docs = tool.get_json_doc() if tool else None
        return docs


    def get_public_tool_docs(self) -> Optional[list[dict]]:
        return [tool.get_json_doc() for tool in self.tool_dict.values() if tool.is_public]


    @staticmethod
    def log(msg : str):
        print(msg)
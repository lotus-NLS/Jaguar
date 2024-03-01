from __future__ import annotations

from hollarek.dev.log import Loggable, LogLevel
from engine.l3_applications import Tool, ToolCall, Application
# ---------------------------------------------------------


class OS(Loggable):
    def __init__(self):
        super().__init__()
        self.tool_call_dict : dict[int,ToolCall] = {}
        self.applications : list[Application] = []


    def handle_calls(self):
        tools_map = self.get_tools_map()
        for tool_call in list(self.tool_call_dict.values()):
            try:
                tool = tools_map[tool_call.name]
                tool.handle(tool_call=tool_call)
            except:
                self.log(f'No tool found with name {tool_call.name}', level=LogLevel.ERROR)
        self.reset_calls()

    # ---------------------------------------------------
    # update

    def reset_calls(self):
        self.tool_call_dict : dict[int,ToolCall] = {}


    def update(self, partial_call : ToolCall):
        the_index = partial_call.index

        call = self.tool_call_dict.get(the_index)
        if call is None:
            self.tool_call_dict[the_index] = partial_call
        else:
            self.tool_call_dict[the_index].update(partial_call=partial_call)


    # ---------------------------------------------------
    # get

    def get_toolcall_made(self) -> bool:
        return not len(self.tool_call_dict) == 0


    def get_docs_map(self, active_only : bool = True) -> dict[str, dict]:
        docs = {}
        for app in self.applications:
            docs.update(app.get_doc_dict(active_only=active_only))
        return docs


    def get_tools_map(self, active_only : bool = True) -> dict[str, Tool]:
        tools = {}
        for app in self.applications:
            tools.update(app.get_tool_dict(active_only=active_only))
        return tools

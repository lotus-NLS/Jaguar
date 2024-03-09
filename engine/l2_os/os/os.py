from __future__ import annotations
from hollarek.logging import Loggable, LogLevel

from engine.l2_os.os.meta_tools import Close, Open
from engine.l4_tools import Tool, CallMap, ToolDoc
from engine.l3_models.generation import Chunk
from engine.l2_os.application import Application

# ---------------------------------------------------------

class OS(Loggable):
    def __init__(self):
        super().__init__()
        self.call_map : CallMap = CallMap()
        self.appliction_map : dict[int, Application] = {}
        self.meta_tools : list[Tool] = [Open(self.appliction_map), Close(self.appliction_map)]

    # ---------------------------------------------------
    # call updates

    def handle_calls(self):
        tools_map = self.get_tool_map()
        for tool_call in list(self.call_map.values()):
            try:
                tool = tools_map[tool_call.name]
                tool.handle(tool_call=tool_call)
            except:
                self.log(f'No tool found with name {tool_call.name}', level=LogLevel.ERROR)
        self.call_map : CallMap = CallMap()

    def store_info(self, chunk : Chunk):
        self.call_map.add(chunk.get_call_map())

    def toolcall_made(self) -> bool:
        return not len(self.call_map) == 0

    # ---------------------------------------------------
    # get

    def get_tool_map(self) -> dict[str, Tool]:
        return {tool.get_name() : tool for tool in self.get_tools()}

    def get_docs(self) -> list[ToolDoc]:
        return [tool.get_doc() for tool in self.get_tools()]

    def get_tools(self) -> list[Tool]:
        tools = self.meta_tools
        active_applications = [app for app in self.appliction_map.values() if app.is_open()]
        for app in active_applications:
            tools += app.get_actions()
        return tools

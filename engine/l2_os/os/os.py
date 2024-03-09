from __future__ import annotations
from hollarek.logging import Loggable, LogLevel

from engine.l4_tools import Tool, CallMap, ToolDoc
from engine.l2_os.application import Application, Tab
from .meta_tools import Close, Open

# ---------------------------------------------------------

class OS(Loggable):
    def __init__(self, tabs : list[Tab]):
        super().__init__()
        self.application_map = {j :  Application(index=j, tab_type=tab_type) for j, tab_type in enumerate(tabs)}
        self.meta_tools : list[Tool] = [Open(self.application_map), Close(self.application_map)]

    # ---------------------------------------------------
    # call updates

    def handle_calls(self, call_map : CallMap):
        tools_map = self.get_tool_map()
        for tool_call in list(call_map.values()):
            try:
                tool = tools_map[tool_call.name]
                tool.handle(tool_call=tool_call)
            except:
                self.log(f'No tool found with name {tool_call.name}', level=LogLevel.ERROR)

    # ---------------------------------------------------
    # get

    def get_tool_map(self) -> dict[str, Tool]:
        return {tool.get_name() : tool for tool in self.get_tools()}

    def get_docs(self) -> list[ToolDoc]:
        return [tool.get_doc() for tool in self.get_tools()]

    def get_tools(self) -> list[Tool]:
        tools = self.meta_tools
        active_applications = [app for app in self.application_map.values() if app.is_open()]
        for app in active_applications:
            tools += app.get_actions()
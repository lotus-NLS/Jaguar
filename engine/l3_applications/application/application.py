from api import Entry, Speaker, Role
from typing import Optional

from .tool import Tool
from .output import WindowMap
from .application_tools import ActionTool, CloseTool

# ---------------------------------------------------


class Application:
    def __init__(self):
        self.window_map : WindowMap = WindowMap()
        self.open_tool : Optional[Tool] = None
        self.action_tools : Optional[list[ActionTool]] = None
        self.close_tool : CloseTool = CloseTool(window_map=self.window_map)

    # ---------------------------------------------------
    #  context

    def get_context(self) -> Entry:
        context = self.get_header()
        for index, window in self.window_map.items():
            context += f'--- {window.name} ---'
            context += window.content
        return self.create_entry(msg=context)



    def get_header(self) -> str:
        header_len = 40
        name = self.__class__.__name__
        num_dashes = max(header_len - len(name), 0)
        dashes = '=' * num_dashes
        return  f'{dashes} {name} {dashes}'

    @classmethod
    def create_entry(cls, msg : str) -> Entry:
        return Entry(speaker=Speaker(role=Role.TOOL, name=cls.__name__), msg=msg)

    # ---------------------------------------------------
    # tools

    def get_docs(self, active_only : bool = Tool) -> list[dict]:
        tools = self.get_tools(active_only=active_only)
        docs = []
        for tool in tools:
            docs += tool.get_json_doc()
        return docs


    def get_tools(self, active_only : bool) -> list[Tool]:
        tools = []
        if self.open_tool:
            tools.append(self.open_tool)
        if self.action_tools:
            tools += self.action_tools
        tools.append(self.close_tool)
        return [tool for tool in tools if tool.is_active] if active_only else tools





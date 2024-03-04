from api import Entry, Speaker, Role
from abc import abstractmethod
from hollarek.logging import Loggable

from .actions import OpeningTool, InteractionTool, CloseTool
from .actions import WindowMap
from engine.l4_tools import Tool, ToolDoc
# ---------------------------------------------------

class Application(Loggable):
    def __init__(self):
        super().__init__()
        self.window_map : WindowMap = WindowMap()
        self.open_tool : Tool = self.create_open_tool()
        self.action_tools : list[InteractionTool] = self.create_action_tools()
        self.close_tool : CloseTool = CloseTool(window_map=self.window_map,call_timeout=0.1)

        self.tools : list[Tool] = [self.open_tool] + self.action_tools + [self.close_tool]
        self.tool_dict : dict[str, Tool] = {tool.get_name() : tool for tool in self.tools}

    # ---------------------------------------------------
    #  context

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    @abstractmethod
    def get_desc(cls):
        pass


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


    @abstractmethod
    def create_open_tool(self) -> OpeningTool:
        pass

    @abstractmethod
    def create_action_tools(self) -> list[InteractionTool]:
        pass


    def get_tools(self, active_only : bool) -> list[Tool]:
        tools = self.tools
        if active_only:
            tools = [tool for tool in tools if tool.is_active]
        return tools


    def get_tool_dict(self, active_only : bool = False):
        tool_dict = self.tool_dict
        if active_only:
            tool_dict = {name : tool for (name, tool) in tool_dict.items() if tool.is_active}
        return tool_dict


    def get_doc_dict(self, active_only : bool = False) -> dict[str, ToolDoc]:
        tools = self.get_tools(active_only=active_only)
        docs = {}
        for tool in tools:
            docs[tool.get_name()] = tool.get_json_doc(application_name=self.get_name())
        return docs


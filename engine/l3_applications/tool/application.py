from api import Entry, Speaker, Role
from abc import abstractmethod
from typing import Optional

from .input import ToolCall
from .output import WindowMap, Window
from .tool import Tool, ToolArg
from abc import ABC
# ---------------------------------------------------


class OpenTool(Tool, ABC):
    def __init__(self, window_map : WindowMap):
        super().__init__(window_map=window_map, call_timeout=1)

    def add_window(self, window: Window):
        index = 0
        while index in self.window_map:
            index += 1
        self.window_map[index] = window


class ActionTool(Tool, ABC):
    def __init__(self, window_map : WindowMap, call_timeout : int):
        super().__init__(window_map=window_map, call_timeout=call_timeout)
        self.index_arg: ToolArg = ToolArg(name='Window index', desc='Window on which to perform action')

    def get_window(self) -> Optional[Window]:
        index = int(self.index_arg.val)
        return self.window_map.get(index)



class CloseTool(Tool):
    def __init__(self, window_map : WindowMap):
        super().__init__(window_map=window_map, call_timeout=1)
        self.index_arg : ToolArg = ToolArg(name='Window index', desc='Window to close')

    def do(self):
        index = int(self.index_arg.val)
        if index not in self.window_map:
            raise ValueError(f'Window index {index} does not exist')
        del self.window_map[index]

    def get_desc(self) -> str:
        return f'Close an open window from associated application'


class Application:
    def __init__(self):
        self.window_map : WindowMap = WindowMap()
        self.open_tool : Tool = self.create_open_tool()
        self.action_tools : list[ActionTool] = self.create_action_tools()
        self.close_tool : CloseTool = CloseTool(window_map=self.window_map)

    @abstractmethod
    def handle(self, tool_call : ToolCall):
        pass

    # ---------------------------------------------------
    #  context

    @classmethod
    def get_name(cls):
        return cls.__name__


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
    def create_open_tool(self) -> OpenTool:
        pass

    @abstractmethod
    def create_action_tools(self) -> list[ActionTool]:
        pass

    def get_docs(self, active_only : bool = Tool) -> list[dict]:
        tools = self.get_tools(active_only=active_only)
        docs = []
        for tool in tools:
            docs += tool.get_json_doc(application_name=self.get_name())
        return docs


    def get_tools(self, active_only : bool) -> list[Tool]:
        tools = []
        if self.open_tool:
            tools.append(self.open_tool)
        if self.action_tools:
            tools += self.action_tools
        tools.append(self.close_tool)
        return [tool for tool in tools if tool.is_active] if active_only else tools

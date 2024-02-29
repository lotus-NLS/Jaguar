from api import Entry, Speaker, Role
from abc import abstractmethod

from .output import WindowMap, Window
from .tool import Tool, ToolArg
# ---------------------------------------------------


class OpenTool(Tool):
    @abstractmethod
    def do(self) -> Window:
        pass

    def add_window(self, window: Window):
        index = 0
        while index in self.window_map:
            index += 1
        self.window_map[index] = window

    @classmethod
    @abstractmethod
    def get_application_name(cls) -> str:
        pass


class ActionTool(Tool):
    def __init__(self, window_map : WindowMap):
        super().__init__(window_map=window_map)
        self.index_arg: ToolArg = ToolArg(name='Window index', desc='Window on which to perform action')

    def do(self) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_application_name(cls) -> str:
        pass

class CloseTool(Tool):
    def __init__(self, window_map : WindowMap):
        super().__init__(window_map=window_map)
        self.index_arg : ToolArg = ToolArg(name='Window index', desc='Index of window to close')

    def do(self):
        index = int(self.index_arg.val)
        if index not in self.window_map:
            raise ValueError(f'Window index {index} does not exist')
        del self.window_map[index]

    @classmethod
    @abstractmethod
    def get_application_name(cls) -> str:
        pass


class Application:
    def __init__(self):
        self.window_map : WindowMap = WindowMap()
        self.open_tool : Tool = self.get_open_tool()
        self.action_tools : list[ActionTool] = self.get_action_tools()
        self.close_tool : CloseTool = CloseTool(window_map=self.window_map)

    # ---------------------------------------------------
    #  context

    @abstractmethod
    def get_open_tool(self) -> OpenTool:
        pass

    def get_action_tools(self) -> list[ActionTool]:
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

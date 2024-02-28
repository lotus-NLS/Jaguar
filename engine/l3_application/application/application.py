from api import Entry, Speaker, Role

from ..tool import Tool
from abc import abstractmethod

# ---------------------------------------------------

class Window:
    def __init__(self, name : str):
        self.name : str = name
        self.content : str = ''

class Application:
    def __init__(self):
        self.window_map : dict[int, Window] = {}
        self.available_tools : dict[str, Tool] = {}
        self.active_tools : dict[str, Tool] = {}


    @abstractmethod
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


    def get_tool_docs(self, active_only = Tool):
        tools = list(self.available_tools.values()) if not active_only else list(self.active_tools.values())
        docs = []
        for tool in tools:
            docs += tool.get_json_doc()
        return docs


    @classmethod
    def create_entry(cls, msg : str) -> Entry:
        return Entry(speaker=Speaker(role=Role.TOOL, name=cls.__name__), msg=msg)


    def add_window(self, window: Window):
        index = 0
        while index in self.window_map:
            index += 1
        self.window_map[index] = window


    def close_window(self, index : int):
        del self.window_map[index]


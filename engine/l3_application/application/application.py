from api import Entry

from ..tool import Tool
from abc import abstractmethod

# ---------------------------------------------------



class Window:
    def __init__(self, name : str):
        self.name : str = name
        self.content : str = ''

    def update_content(self, new_content : str):
        self.content = new_content


class Application:
    def __init__(self):
        self.window_map : dict[int, Window] = {}
        self.tools : dict[str, Tool] = {}
        self.active_tools : dict[str, Tool] = {}


    @abstractmethod
    def get_context(self) -> Entry:
        pass


    def add_window(self, window: Window):
        index = 0
        while index in self.window_map:
            index += 1
        self.window_map[index] = window


    def close_window(self, index : int):
        del self.window_map[index]


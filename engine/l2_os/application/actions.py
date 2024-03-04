from abc import abstractmethod
from .window import Window, WindowMap
from typing import TypeVar

from engine.l4_tools import Tool, ToolArg, ToolCall
WindowType = TypeVar('WindowType', bound=Window)
# ---------------------------------------------------


class OpeningTool(Tool):
    def __init__(self, window_map : WindowMap):
        super().__init__(call_timeout=1)
        self.window_map : WindowMap = window_map

    @classmethod
    @abstractmethod
    def get_desc(cls) -> str:
        pass


    def do(self):
        self.add_window(window=self.get_window())

    @abstractmethod
    def get_window(self) -> Window:
        pass

    def add_window(self, window: Window):
        index = 0
        while index in self.window_map:
            index += 1
        self.window_map[index] = window


class InteractionTool(Tool):
    def __init__(self, window_map: WindowMap, call_timeout : float = 20):
        super().__init__(call_timeout=call_timeout)
        self.window_map : WindowMap = window_map
        self.index_arg: ToolArg = ToolArg(name='window_index', desc='Index of window on which to perform action'
                                          , choices=[str(index) for index in window_map.keys()])


    def get_window(self) -> WindowType:
        index = int(self.index_arg.val)
        return self.window_map.get(index)

    def _set_args(self, tool_call : ToolCall):
        self.index_arg.choices = [str(index) for index in self.window_map.keys()]
        super()._set_args(tool_call=tool_call)

    @abstractmethod
    def do(self):
        pass

    @classmethod
    @abstractmethod
    def get_desc(cls) -> str:
        pass


class CloseTool(InteractionTool):
    def __init__(self, window_map : WindowMap, call_timeout : float):
        super().__init__(window_map=window_map, call_timeout=call_timeout)
        self.index_arg.desc = f'Index of window to close'
        self.window_map : WindowMap = window_map

    def do(self):
        index = int(self.index_arg.val)
        if index not in self.window_map:
            raise ValueError(f'Window index {index} does not exist')
        del self.window_map[index]

    @classmethod
    def get_desc(cls) -> str:
        return f'Close an open window from associated application'


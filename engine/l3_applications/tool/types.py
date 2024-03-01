from abc import abstractmethod, ABC

from .tool import Tool, WindowMap, ToolArg
from .output import Window

# ---------------------------------------------------

class OpenTool(Tool):
    def __init__(self, window_map : WindowMap):
        super().__init__(call_timeout=1)
        self.window_map : WindowMap = window_map

    def do(self):
        self.add_window(window=self.get_window())


    def add_window(self, window: Window):
        index = 0
        while index in self.window_map:
            index += 1
        self.window_map[index] = window


    @abstractmethod
    def get_window(self) -> Window:
        pass


class ActionTool(Tool):
    def __init__(self, window_map : WindowMap, call_timeout : int):
        super().__init__(call_timeout=call_timeout)
        self.index_arg: ToolArg = ToolArg(name='Window index', desc='Window on which to perform action')
        self.window_map : WindowMap = window_map

    def get_window(self):
        index = int(self.index_arg.val)
        return self.window_map.get(index)

    @abstractmethod
    def do(self):
        pass


class CloseTool(Tool):
    def __init__(self, window_map : WindowMap):
        super().__init__(call_timeout=1)
        self.index_arg : ToolArg = ToolArg(name='Window index', desc='Window to close')
        self.window_map : WindowMap = window_map

    def do(self):
        index = int(self.index_arg.val)
        if index not in self.window_map:
            raise ValueError(f'Window index {index} does not exist')
        del self.window_map[index]

    def get_desc(self) -> str:
        return f'Close an open window from associated application'

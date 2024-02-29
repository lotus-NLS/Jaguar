from abc import abstractmethod

from engine.l3_applications.application import Tool, Window, ToolArg
from engine.l3_applications.application.output import WindowMap


class OpenTool(Tool):
    @abstractmethod
    def do(self) -> Window:
        pass

    def add_window(self, window: Window):
        index = 0
        while index in self.window_map:
            index += 1
        self.window_map[index] = window


class ActionTool(Tool):
    def __init__(self, window_map : WindowMap):
        super().__init__(window_map=window_map)
        self.index_arg: ToolArg = ToolArg(name='Window index', desc='Window on which to perform action')

    def do(self) -> None:
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

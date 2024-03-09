from engine.l4_tools import Tool, ToolArg, ToolCall
from .window import Tab
from abc import ABC, abstractmethod
# ---------------------------------------------------------

class Action(Tool, ABC):
    def __init__(self, tab_map: dict[int,Tab], call_timeout : float = 20):
        super().__init__(call_timeout=call_timeout)
        self.tab_map : dict[int,Tab] = tab_map
        self.index_arg: ToolArg = ToolArg(name='tab_index')

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def get_desc(self) -> str:
        pass

    def get_tab(self):
        return self.tab_map[int(self.index_arg.get_value())]

    def _set_args(self, tool_call : ToolCall):
        self.index_arg.choices = [str(index) for index in self.tab_map.keys()]
        super()._set_args(tool_call=tool_call)

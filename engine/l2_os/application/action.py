from engine.l4_tools import Tool, ToolArg, ToolCall, ToolDoc
from .window import Tab
from abc import ABC, abstractmethod
# ---------------------------------------------------------

class Action(Tool, ABC):
    def __init__(self, app_name : str, tabs: dict[int,Tab], call_timeout : float = 20):
        super().__init__(call_timeout=call_timeout)
        self.tabs : dict[int,Tab] = tabs
        self.index_arg: ToolArg = ToolArg(name='tab_index')
        self.app_name : str = app_name

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def get_desc(self) -> str:
        pass

    def _set_args(self, tool_call : ToolCall):
        self.index_arg.choices = [str(index) for index in self.tabs.keys()]
        super()._set_args(tool_call=tool_call)

    def get_doc(self, *args, **kwargs) -> ToolDoc:
        return super().get_doc(app_name=self.app_name)


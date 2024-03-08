from abc import abstractmethod

from engine.l4_tools import Tool, ToolArg, ToolCall, ToolDoc
from .window import Tabs, Tab


class Action(Tool):
    def __init__(self, app_name : str, tabs: Tabs, call_timeout : float = 20):
        super().__init__(call_timeout=call_timeout)
        self.tabs : Tabs = tabs
        self.index_arg: ToolArg = ToolArg(name='window_index', desc='Index of window on which to perform action'
                                          ,choices=[str(index) for index in tabs.keys()])
        self.app_name : str = app_name


    def get_window(self) -> Tab:
        index = int(self.index_arg.val)
        return self.tabs.get(index)

    def _set_args(self, tool_call : ToolCall):
        self.index_arg.choices = [str(index) for index in self.tabs.keys()]
        super()._set_args(tool_call=tool_call)

    def get_doc(self, *args, **kwargs) -> ToolDoc:
        return super().get_doc(app_name=self.app_name)

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def get_desc(self) -> str:
        pass


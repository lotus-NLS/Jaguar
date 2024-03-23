from engine.l4_tools import Tool, ToolArg, ToolCall
from .window import Workspace
from abc import ABC, abstractmethod
# ---------------------------------------------------------

class Action(Tool, ABC):
    def __init__(self, workspace: Workspace, call_timeout : float = 20):
        super().__init__(call_timeout=call_timeout)
        self.workspace : Workspace = workspace

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def get_desc(self) -> str:
        pass

    def _set_args(self, tool_call : ToolCall):
        super()._set_args(tool_call=tool_call)

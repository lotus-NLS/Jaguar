from __future__ import annotations

from engine.l3_aos.workspaces import Workspace
from engine.l3_aos.tools import ToolCallMap, ToolOutput, Tool, ToolDoc
from holytools.logging import Loggable, LogLevel


# ---------------------------------------------------------

class AOS(Loggable):
    def __init__(self, workspaces : list[Workspace]):
        super().__init__()
        self.workspace_map : dict[int, Workspace] = {j : w for (j, w) in enumerate(workspaces)}

    # ---------------------------------------------------
    # call updates

    def handle_calls(self, call_map : ToolCallMap) -> list[ToolOutput]:
        if call_map.is_empty():
            return []

        tools_map = {tool.get_name() : tool for tool in self.get_tools()}
        outputs = []
        for tool_call in list(call_map.values()):
            try:
                tool = tools_map[tool_call.name]
                outputs += [tool.handle(tool_call=tool_call)]
            except KeyError:
                self.log(f'No tool found with name {tool_call.name}', level=LogLevel.ERROR)
                outputs += [ToolOutput.not_found(name=tool_call.name)]
            except Exception as e:
                outputs += [ToolOutput.failed(name=tool_call.name, reason=e)]
        return outputs

    # ---------------------------------------------------
    # get

    def get_tools(self) -> list[Tool]:
        tools = []
        for workspace in self.get_workspaces():
            tools += workspace.get_actions()
        return tools

    def get_docs(self) -> list[ToolDoc]:
        docs = []
        for workspace in self.get_workspaces():
            docs += workspace.get_docs()
        return docs

    def get_workspaces(self) -> list[Workspace]:
        return [workspace for workspace in self.workspace_map.values()]
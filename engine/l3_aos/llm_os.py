from __future__ import annotations

from engine.l3_aos.tools import ToolOutput, Tool, ToolDoc
from engine.l3_aos.workspace import Workspace
from holytools.logging import Loggable, LogLevel


# ---------------------------------------------------------

class AOS(Loggable):
    def __init__(self, workspaces : list[Workspace]):
        super().__init__()
        self.workspace_map : dict[int, Workspace] = {j : w for (j, w) in enumerate(workspaces)}


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
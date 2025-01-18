from __future__ import annotations

from engine.l3_aos.workspaces.terminal import Terminal
from engine.l3_aos.tools import Tool, ToolDoc
from engine.l3_aos.workspace import Workspace
from engine.l3_aos.workspaces.workflowy import Workflowy
from holytools.logging import Loggable


# ---------------------------------------------------------

class AOS(Loggable):
    def __init__(self, workspaces : list[Workspace], workflowy : Workflowy = Workflowy()):
        super().__init__()
        self._workspaces : list[Workspace] = workspaces + [workflowy]
        self.workflowy : Workflowy = workflowy
        self._check_ws_uniqueness()

    @classmethod
    def terminal_only(cls) -> AOS:
        return cls(workspaces=[Terminal()])

    def add_workspace(self, ws : Workspace):
        self._workspaces.append(ws)
        self._check_ws_uniqueness()

    def workspace_engage(self) -> bool:
        return not self.workflowy.root is None

    def _check_ws_uniqueness(self):
        ws_namelist = [workspace.get_name() for workspace in self._workspaces]
        ws_nameset = set(ws_namelist)
        if len(ws_namelist) != len(ws_nameset):
            raise ValueError('Workspace names must be unique')

    # ---------------------------------------------------
    # get

    def get_tools(self) -> list[Tool]:
        tools = []
        for workspace in self.get_workspaces():
            tools += workspace.get_actions()
        return tools

    def get_action_docs(self) -> list[ToolDoc]:
        docs = []
        for workspace in self.get_workspaces():
            docs += workspace.get_action_docs()
        return docs

    def get_workspaces(self) -> list[Workspace]:
        return self._workspaces
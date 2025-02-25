from __future__ import annotations

from engine.l3_aos.tools import Tool
from engine.l3_aos.workspaces import Workspace
from engine.l3_aos.workspaces.terminal import Terminal


# ---------------------------------------------------------

class AOS:
    def __init__(self, workspaces : list[Workspace], cautious_mode : bool = False):
        super().__init__()
        self.workspaces : list[Workspace] = []
        for ws in workspaces:
            self.add_workspace(ws)
        self.cautious_mode : bool = cautious_mode

    def add_workspace(self, ws : Workspace):
        self.workspaces.append(ws)
        ws_namelist = [workspace.get_name() for workspace in self.workspaces]
        ws_nameset = set(ws_namelist)
        if len(ws_namelist) != len(ws_nameset):
            raise ValueError('Workspace names must be unique')

    @classmethod
    def terminal_only(cls) -> AOS:
        return cls(workspaces=[Terminal()])

    # ------------------------------------------------------------------
    # get

    def get_tools(self) -> list[Tool]:
        workspaces = self.get_workspaces()
        tools = []
        for ws in workspaces:
            tools += ws.get_actions()
        return tools

    def find_ws(self, name : str) -> Workspace:
        ws_map = {ws.get_name(): ws for ws in self.get_workspaces()}
        return ws_map[name]

    def get_workspaces(self, active_only : bool = False) -> list[Workspace]:
        workspaces = self.workspaces
        if active_only:
            workspaces = [ws for ws in workspaces if ws.is_active]

        return workspaces

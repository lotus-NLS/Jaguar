from __future__ import annotations

from engine.l3_aos.workspace import Workspace
from engine.l3_aos.workspaces.terminal import Terminal


# ---------------------------------------------------------

class AOS:
    def __init__(self, workspaces : list[Workspace]):
        super().__init__()
        self.workspaces : list[Workspace] = workspaces
        self._check_ws_uniqueness()

    @classmethod
    def terminal_only(cls) -> AOS:
        return cls(workspaces=[Terminal()])

    def add_workspace(self, ws : Workspace):
        self.workspaces.append(ws)
        self._check_ws_uniqueness()

    def _check_ws_uniqueness(self):
        ws_namelist = [workspace.get_name() for workspace in self.workspaces]
        ws_nameset = set(ws_namelist)
        if len(ws_namelist) != len(ws_nameset):
            raise ValueError('Workspace names must be unique')

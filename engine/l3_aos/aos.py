from __future__ import annotations

from engine.l3_aos.tools import Tool, ToolArg
from engine.l3_aos.workspace import Workspace
from engine.l3_aos.workspaces.terminal import Terminal


# ---------------------------------------------------------

class AOS:
    def __init__(self, workspaces : list[Workspace]):
        super().__init__()
        self.workspaces : list[Workspace] = []
        for ws in workspaces:
            self.add_workspace(ws)
        self.update_tool : UpdateTool = UpdateTool()

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

    def get_tools(self, with_update : bool = False) -> list[Tool]:
        workspaces = self.get_workspaces()
        tools = []
        for ws in workspaces:
            tools += ws.get_actions()
        if with_update:
            tools += [self.update_tool]
        return tools

    def get_ws(self, name : str) -> Workspace:
        ws_map = {ws.get_name(): ws for ws in self.get_workspaces()}
        return ws_map[name]

    def get_workspaces(self, active_only : bool = False) -> list[Workspace]:
        workspaces = self.workspaces
        if active_only:
            workspaces = [ws for ws in workspaces if ws.is_active]

        return workspaces

    def get_headline(self) -> str:
        return self.update_tool.headline.get_value()


class UpdateTool(Tool):
    def  __init__(self):
        super().__init__()
        self.headline : ToolArg = ToolArg(name='Action headline')

    def do(self):
        pass

    def get_desc(self) -> str:
        return (f'Allows you to report the current action youre taking in this step. '
                f'Collectively these updates generate a timeline of your actions.')

    def get_args(self) -> list[ToolArg]:
        return [self.headline]
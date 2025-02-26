from __future__ import annotations

from engine.l3_aos.tools import Tool, ToolCall, ToolOutput
from engine.l3_aos.workspaces import Workspace
from engine.l3_aos.workspaces.terminal import Terminal
from holytools.logging import Loggable


# ---------------------------------------------------------

class AOS(Loggable):
    def __init__(self, workspaces : list[Workspace], cautious_mode : bool = False):
        super().__init__()
        self.workspaces : list[Workspace] = []
        for ws in workspaces:
            self.add_workspace(ws)
        self.cautious_mode : bool = cautious_mode

    def execute(self, tool_calls : list[ToolCall]) -> list[ToolOutput]:
        outputs: list[ToolOutput] = []
        tools_map = {t.get_name(): t for t in self.get_tools()}

        if self.cautious_mode and len(tool_calls) > 0:
            tool_calls_report = [f'{call.name} with args {call.json_str}' for call in tool_calls]
            notice_str = f'Following tool call(s) requests permission:'
            for r in tool_calls_report:
                notice_str += f'\n- {r}'
            notice_str += f'\n- Allow execution? (y/n)'
            user_input = input(notice_str)
            if user_input.lower() != 'y':
                return [ToolOutput.failed(reason='Execution was denied')]

        for call in tool_calls:
            try:
                tool = tools_map[call.name]
                outputs += [tool.execute(tool_call=call)]
            except KeyError as e:
                self.error(f'No tool found with name {call.name}')
                outputs += [ToolOutput.exception(name=call.name, reason=e)]
            except Exception as e:
                self.error(f'Error while executing tool {call.name}: {e.__repr__()}')
                outputs += [ToolOutput.exception(name=call.name, reason=e)]
        return outputs

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

from __future__ import annotations

from typing import Optional

from engine.l3_aos.browser import Browser
from engine.l3_aos.ide import PythonIDE
from engine.l3_aos.terminal import Terminal
from engine.l3_aos.tools import Tool, ToolCall, ToolOutput, ToolDoc
from engine.l3_aos.workspace import Workspace

# ---------------------------------------------------------

class AOS:
    def __init__(self, browser : Optional[Browser] = None, terminal : Optional[Terminal] = None, ide : Optional[PythonIDE] = None):
        super().__init__()

        self.browser : Optional[Browser] = browser
        self.terminal : Optional[Terminal] = terminal
        self.ide : Optional[PythonIDE] = ide

        self.workspaces : list[Workspace] = []
        for ws in [ws for ws in [terminal, browser, ide] if ws is not None]:
            self.add_workspace(ws)

    def process(self, tool_calls : list[ToolCall]) -> list[ToolOutput]:
        outputs: list[ToolOutput] = []
        tools_map = {t.get_name(): t for t in self.get_tools()}

        for call in tool_calls:
            try:
                tool = tools_map[call.name]
                outputs.append(tool.execute(args_dict=call.get_args_dict()))
            except KeyError:
                err = KeyError(f'No tool found with name {call.name}')
                outputs.append(ToolOutput.exception(name=call.name, reason=err))
            except Exception as e:
                err = RuntimeError(f'An error occured while executing tool {call.name}: {e.__repr__()}')
                outputs.append(ToolOutput.exception(name=call.name, reason=err))
        return outputs

    def add_workspace(self, ws : Workspace):
        self.workspaces.append(ws)
        ws_namelist = [workspace.get_name() for workspace in self.workspaces]
        ws_nameset = set(ws_namelist)
        if len(ws_namelist) != len(ws_nameset):
            raise ValueError('Workspace names must be unique')

    @classmethod
    def empty(cls) -> AOS:
        return cls(browser=None, terminal=None, ide=None)

    @classmethod
    def full(cls, google_api_key : str, searchengine_id : str) -> AOS:
        return cls(browser=Browser(google_api_key=google_api_key, searchengine_id=searchengine_id), terminal=Terminal(), ide=PythonIDE())

    @classmethod
    def terminal_only(cls) -> AOS:
        return cls(terminal=Terminal())

    # ------------------------------------------------------------------
    # get

    def get_docs(self, required_tool : Optional[Tool] = None) -> list[ToolDoc]:
        tools = self.get_tools() if required_tool is None else [required_tool]
        docs = [tool.get_doc() for tool in tools]
        return docs

    def get_tools(self) -> list[Tool]:
        workspaces = self.get_workspaces()
        tools : list[Tool] = []
        for ws in workspaces:
            tools += ws.get_actions()
        return tools

    def find_ws(self, name : str) -> Workspace:
        ws_map = {ws.get_name(): ws for ws in self.get_workspaces()}
        return ws_map[name]

    def get_workspaces(self, include_system_opened : bool = False) -> list[Workspace]:
        def is_included(ws : Workspace):
            if include_system_opened:
                return True
            if not ws.is_system_opened():
                return True
            else:
                return ws.is_open

        return [ws for ws in self.workspaces if is_included(ws)]

    def get_ws(self, name : str) -> Workspace:
        ws_dict = {ws.get_name(): ws for ws in self.workspaces}
        return ws_dict[name]
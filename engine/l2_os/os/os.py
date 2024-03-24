from __future__ import annotations
from hollarek.core.logging import Loggable, LogLevel

from engine.l4_tools import Tool, CallMap, ToolDoc, ToolOutput
from engine.l3_models import Context
from engine.l2_os.workspaces import Workspace
from func_timeout import func_timeout, FunctionTimedOut
# ---------------------------------------------------------

class OS(Loggable):
    def __init__(self, workspace_types : list[type[Workspace]]):
        super().__init__()
        self.workspaces : dict[int, Workspace] = {j : workspace_type() for (j, workspace_type) in  enumerate(workspace_types)}

    # ---------------------------------------------------
    # call updates

    def handle_calls(self, call_map : CallMap) -> list[ToolOutput]:
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

    def get_context(self) -> Context:
        open_workspaces = [workspace for workspace in self.get_workspaces() if workspace.is_active]
        entries = []
        for workspace in open_workspaces:
            try:
                entry = func_timeout(func=workspace.get_entry, timeout=10)
                entries.append(entry)
            except FunctionTimedOut:
                self.error(f'Workspace get entry out timed for workspace \"{workspace.get_name()}\"')
            except BaseException as e:
                self.error(f'Error in getting entry for app \"{workspace.get_name()}\": {e}')
        docs = self._get_docs()
        return Context(entries=entries, docs=docs)


    def get_tools(self) -> list[Tool]:
        tools = []
        for workspace in self.get_workspaces():
            tools += workspace.get_actions()
        return tools


    def _get_docs(self) -> list[ToolDoc]:
        docs = []
        for workspace in self.get_workspaces():
            docs += workspace.get_docs()
        return docs

    def get_workspaces(self) -> list[Workspace]:
        return [workspace for workspace in self.workspaces.values()]
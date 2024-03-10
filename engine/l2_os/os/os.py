from __future__ import annotations
from hollarek.logging import Loggable, LogLevel

from engine.l4_tools import Tool, CallMap, ToolDoc, ToolOutput
from engine.l3_models import Context
from engine.l2_os.application import Application, Workspace
from .meta_tools import Close, Open


# ---------------------------------------------------------

class OS(Loggable):
    def __init__(self, workspace_types : list[type[Workspace]]):
        super().__init__()
        self.app_map = {}
        for j, workspace_type in enumerate(workspace_types):
            self.app_map[j] = Application(index=j, workspace_type=workspace_type)

        self.open : Tool = Open(self.app_map)
        self.close : Tool = Close(self.app_map)
        self.meta_tools : list[Tool] = [self.open, self.close]

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
        open_apps = [app for app in self.app_map.values() if app.is_open()]
        entries = []
        for app in open_apps:
            try:
                entry = app.window.get_entry()
                entries.append(entry)
            except:
                self.log(f'Error in getting entry for app \"{app.get_name()}\"', level=LogLevel.ERROR)
        docs = self._get_docs()
        return Context(entries=entries, docs=docs)


    def get_tools(self) -> list[Tool]:
        tools = self.meta_tools
        active_applications = [app for app in self.app_map.values() if app.is_open()]
        for app in active_applications:
            tools += app.get_actions()
        return tools


    def _get_docs(self) -> list[ToolDoc]:
        docs = [tool.get_doc() for tool in self.meta_tools]
        active_applications = [app for app in self.app_map.values() if app.is_open()]
        for app in active_applications:
            docs += app.get_docs()
        return docs



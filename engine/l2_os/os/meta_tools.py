from __future__ import annotations

from abc import abstractmethod
from engine.l2_os import Application
from engine.l4_tools import Tool, ToolArg, ToolCall
# ---------------------------------------------------------


class MetaTool(Tool):
    def __init__(self, application_map : dict[int,Application]):
        super().__init__()
        self.map: dict[int, Application] = application_map
        self.application_arg: ToolArg = ToolArg(name='application_index', desc='Index of window/application to close')

    def get_application(self) -> Application:
        index = int(self.application_arg.input)
        if index not in self.map:
            raise ValueError(f'Window index {index} does not exist')
        return self.map[index]

    def _set_args(self, tool_call : ToolCall):
        self.application_arg.choices = self.get_choices()
        super()._set_args(tool_call=tool_call)


    @abstractmethod
    def get_choices(self):
        pass


class Close(MetaTool):
    def __init__(self, application_map : dict[int,Application]):
        super().__init__(application_map=application_map)
        self.tab_arg : ToolArg = ToolArg(name='tab_index', desc='Index of tab to close', is_optional=True)

    def get_desc(self) -> str:
        return f'Close an open window from associated application'

    def get_choices(self):
        return [str(index) for index, app in self.map.items() if app.is_open()]

    # ---------------------------------------------------
    # do

    def do(self):
        tab_index = int(self.tab_arg.input) if self.tab_arg.input else None
        application = self.get_application()
        if tab_index:
            application.window.close_tab(tab_index)
        else:
            application.close()


class Open(Tool):
    def __init__(self, app: Application):
        super().__init__()
        self.app : Application = app
        workspace_type = self.app.workspace_type
        uri_name = workspace_type.get_init_argname()
        if uri_name:
            print(f'Uri name for application {self.app.get_name()} is {uri_name}')
            self.uri_arg : ToolArg = ToolArg(name=uri_name)


    def get_desc(self) -> str:
        return f'Opens the application {self.app.get_name}'

    def get_name(self) -> str:
        return f'Open_{self.app.get_name()}'

    # ---------------------------------------------------
    # do

    def do(self):
        self.app.open(uri=self.uri_arg.input)

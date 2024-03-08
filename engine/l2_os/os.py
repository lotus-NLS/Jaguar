from __future__ import annotations

from hollarek.logging import Loggable, LogLevel
from engine.l4_tools import Tool, CallMap, ToolArg, ToolCall, ToolDoc
from engine.l3_models.generation import Chunk
from engine.l2_os.application import Application

# ---------------------------------------------------------


class OS(Loggable):
    def __init__(self):
        super().__init__()
        self.call_map : CallMap = CallMap()
        self.appliction_map : dict[int, Application] = {}
        self.meta_tools : list[Tool] = [Open(self.appliction_map), Close(self.appliction_map)]

    # ---------------------------------------------------
    # call updates

    def handle_calls(self):
        tools_map = self.get_tool_map()
        for tool_call in list(self.call_map.values()):
            try:
                tool = tools_map[tool_call.name]
                tool.handle(tool_call=tool_call)
            except:
                self.log(f'No tool found with name {tool_call.name}', level=LogLevel.ERROR)
        self.reset_calls()


    def store_info(self, chunk : Chunk):
        self.call_map.add(chunk.get_call_map())


    def reset_calls(self):
        self.call_map : CallMap = CallMap()

    def toolcall_made(self) -> bool:
        return not len(self.call_map) == 0

    # ---------------------------------------------------
    # get

    def get_tool_map(self) -> dict[str, Tool]:
        return {tool.get_name() : tool for tool in self.get_tools()}


    def get_tool_docs(self) -> list[ToolDoc]:
        return [tool.get_doc() for tool in self.get_tools()]

    def get_tools(self) -> list[Tool]:
        tools = self.meta_tools
        active_applications = [app for app in self.appliction_map.values() if app.is_active()]
        for app in active_applications:
            tools += app.get_actions()
        return tools


class Close(Tool):
    def __init__(self, application_map : dict[int,Application]):
        super().__init__()
        self.application_map : dict[int, Application] = application_map
        self.window_arg : ToolArg = ToolArg(name='window_index', desc='Index of window to close'
                                           ,choices=self.get_window_indices())
        self.tab_arg : ToolArg = ToolArg(name='tab_index', desc='Index of tab to close')

    @classmethod
    def get_desc(cls) -> str:
        return f'Close an open window from associated application'

    def _set_args(self, tool_call : ToolCall):
        self.window_arg.choices = self.get_window_indices()
        super()._set_args(tool_call=tool_call)

    def get_window_indices(self) -> list[str]:
        return [str(index) for index, app in enumerate(self.application_map)]

    # ---------------------------------------------------
    # do

    def do(self):
        window_index = int(self.window_arg.val)
        tab_index = int(self.tab_arg.val) if self.tab_arg.val else None
        application = self.application_map.get(window_index)

        if tab_index:
            application.close_tab(tab_index)
        else:
            application.close()

    def get_application(self):
        index = int(self.window_arg.val)
        if index not in self.application_map:
            raise ValueError(f'Window index {index} does not exist')
        return self.application_map[index]



class Open(Tool):
    def __init__(self, application_map: dict[int, Application]):
        super().__init__()
        self.application_map: dict[int, Application] = application_map
        self.uri_arg : ToolArg = ToolArg(name='uri', desc='URI argument passed to application')
        choices = [str(i) for i in range(len(self.application_map))]
        self.name_arg : ToolArg = ToolArg(name='index', desc='index of application to open', choices=choices)

    @classmethod
    def get_desc(cls) -> str:
        return f'Open an application'

    # ---------------------------------------------------
    # do

    def do(self):
        application = self.application_map.get(int(self.name_arg.val))
        if not application:
            raise ValueError(f'No application found with index {self.name_arg.val}')
        application.open(uri=self.uri_arg.val)

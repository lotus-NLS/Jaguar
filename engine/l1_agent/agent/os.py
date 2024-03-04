from __future__ import annotations

from hollarek.logging import Loggable, LogLevel
from engine.l3_applications import Tool, ToolCall, Application
from engine.l2_models.generation import Chunk
# ---------------------------------------------------------


class OS(Loggable):
    def __init__(self):
        super().__init__()
        self.call_map : dict[int,ToolCall] = {}
        self.applications : list[Application] = []


    def handle_calls(self):
        tools_map = self.get_tools_map()
        for tool_call in list(self.call_map.values()):
            try:
                tool = tools_map[tool_call.name]
                tool.handle(tool_call=tool_call)
            except:
                self.log(f'No tool found with name {tool_call.name}', level=LogLevel.ERROR)
        self.reset_calls()


    def store_info(self, chunk : Chunk):
        chunk_call_map = chunk.get_call_map()
        for index in chunk_call_map:
            call = chunk_call_map[index]
            if not index in self.call_map:
                self.call_map[index] = call
            else:
                self.call_map[index].update(partial_call=call)
    # ---------------------------------------------------
    # update

    def reset_calls(self):
        self.call_map : dict[int,ToolCall] = {}


    # ---------------------------------------------------
    # get

    def get_toolcall_made(self) -> bool:
        return not len(self.call_map) == 0


    def get_docs(self, active_only : bool = True) -> list[dict]:
        docs = []
        for app in self.applications:
            docs.append(app.get_doc_dict(active_only=active_only))
        return docs


    def get_tools_map(self, active_only : bool = True) -> dict[str, Tool]:
        tools = {}
        for app in self.applications:
            tools.update(app.get_tool_dict(active_only=active_only))
        return tools

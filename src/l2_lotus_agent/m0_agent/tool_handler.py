from typing import Optional
from src.l2_lotus_agent.m2_tool_interface import ToolInterface as Tool
from src.l2_lotus_agent.m1_models import ToolAction


class ToolHandler:
    def __init__(self):
        self.tool_dict : dict[str,Tool] = {}



    def use_tool(self, tool_action : ToolAction):
        print('[Debug]: Agent requested tool usage')
        tool_name = tool_action.get_tool_name()
        tool_args_dict = tool_action.get_arguments_()

        if tool_name in self.tool_dict:
            self.tool_dict[tool_name].handle_call(args_dict=tool_args_dict)

    def get_all_tools(self) -> list[Tool]:
        return list(self.tool_dict.values())

    def get_tool_doc(self, tool_name : str) -> dict:
        return self.tool_dict[tool_name].get_json_doc()

    def get_public_tool_docs(self) -> Optional[list[dict]]:
        return [tool.get_json_doc() for tool in self.tool_dict.values() if tool.is_public_tool]

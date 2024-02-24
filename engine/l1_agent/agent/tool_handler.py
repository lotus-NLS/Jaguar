from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Optional, Callable, Dict, Any, Union

from engine.l1_agent.llm import MultiToolCall
# ---------------------------------------------------------


class ToolHandler:
    def __init__(self):
        self.tool_dict : dict[str,ToolInterface] = {}
        self.multi_tool_call : Optional[MultiToolCall] = None

    def reset_toolcall(self):
        self.multi_tool_call = MultiToolCall()

    def tool_call_requested(self) -> bool:
        return not len(self.multi_tool_call.get_as_list()) == 0

    def execute_multitool_calls(self):
        for tool_call in self.multi_tool_call.get_as_list():
            logging.info(f'Agent requested tool usage with args {tool_call}')

            try:
                tool_call.try_parse_json()

            except:
                logging.error(f'An occured while trying to parse tool json str: {tool_call.json_str}')

            try:
                tool_name = tool_call.get_tool_name()
                tool_args_dict = tool_call.get_arguments()

                if tool_name in self.tool_dict:
                    self.tool_dict[tool_name].handle_call(args_dict=tool_args_dict)
            except Exception as e:
                logging.error(f'An error occured while trying handle tool call: {e}',exc_info=True)

    def get_all_tools(self) -> list[ToolInterface]:
        return list(self.tool_dict.values())

    def get_tool_doc(self, name : str) -> Optional[dict]:
        tool = self.tool_dict.get(name)
        docs = tool.get_json_doc() if tool else None
        return docs

    def get_public_tool_docs(self) -> Optional[list[dict]]:
        return [tool.get_json_doc() for tool in self.tool_dict.values() if tool.is_public_tool]



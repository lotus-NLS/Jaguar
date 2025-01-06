import json
import time

from engine.l3_aos.tools import ToolCall, Tool, ToolArg
from holytools.devtools import Unittest


# ---------------------------------------------------------


class BaseTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.valid_tool_call = ToolCall(json_str=MockToolCalls.valid_printer_args)
        cls.invalid_tool_call = ToolCall(json_str=MockToolCalls.invalid_printer_args)
        cls.empty_tool_call = ToolCall(json_str=MockToolCalls.empty_args_json)

    def setUp(self):
        self.simple_tool : Tool = PrinterTool()
        self.invalid_tool : Tool = InvalidTool()


class MockToolCalls:
    valid_printer_args = json.dumps({f'arg_one': 'value'})
    invalid_printer_args = json.dumps({'arg_onee': ''})
    empty_args_json = json.dumps({})


class InvalidTool(Tool):
    def get_desc(self) -> str:
        return 'throws error on execution'

    def do(self):
        raise ValueError


class PrinterTool(Tool):
    def __init__(self, call_timeout: float = 60):
        super().__init__(call_timeout=call_timeout)
        self.text_arg : ToolArg = ToolArg(name="arg_one")
        self.text_arg_two : ToolArg = ToolArg(name="arg_two", is_optional=True)

    def do(self):
        time.sleep(0.1)
        msg = f"SimpleTool says: {self.text_arg.input}"
        print(msg)
        return msg

    def get_desc(self) -> str:
        return "SimpleTool is a basic implementation for testing."

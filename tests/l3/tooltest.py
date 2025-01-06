import json
import time

from engine.l3_os.tools import Tool, ToolArg
from engine.l3_os.tools import ToolCall
from holytools.devtools import Unittest


# ---------------------------------------------------------


class BaseTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.valid_tool_call = ToolCall(json_str=MockToolCalls.valid_printer_args)
        cls.invalid_tool_call = ToolCall(json_str=MockToolCalls.invalid_printer_args)
        cls.empty_tool_call = ToolCall(json_str=MockToolCalls.empty_args_json)

    def setUp(self):
        self.simple_tool = PrinterTool()
        self.invalid_tool = InvalidTool()


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


# You may want to extend testing to use simple tests like this
# class Greet(Tool):
#     def __init__(self, call_timeout: float = 1):
#         super().__init__(call_timeout=call_timeout)
#         self.text_arg : ToolArg = ToolArg(name="text",
#                                           desc='This is the text that will be displayed to the guests on the monitor.'
#                                                'There is only one monitor so you need only call this once')
#
#     def do(self):
#         print(self.text_arg.input)
#
#     def get_desc(self) -> str:
#         return "This tool is connected with a monitor in our house and allows you to send a message to our guests"
#
#
# class NotifyChef(Tool):
#     def __init__(self, call_timeout: float = 1):
#         super().__init__(call_timeout=call_timeout)
#         self.number_of_guests_arg : ToolArg = ToolArg(name="number_of_guests")
#
#     def do(self):
#         print(f'We need to prepare food for {self.number_of_guests_arg.input} guests')
#
#     def get_desc(self) -> str:
#         return "This tool will notify the chec of the number of guests that we need to prepare food for"

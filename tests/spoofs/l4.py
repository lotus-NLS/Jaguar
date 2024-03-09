from engine.l4_tools import Tool, ToolArg
import time
import json



class SpoofPrinter(Tool):
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


class SpoofErrorRaiser(Tool):
    def get_desc(self) -> str:
        return 'throws error on execution'

    def do(self):
        raise ValueError

class SpoofToolCall:
    valid_printer_args = json.dumps({f'arg_one': 'value'})
    invalid_printer_args = json.dumps({'arg_onee': ''})
    empty_args_json = json.dumps({})
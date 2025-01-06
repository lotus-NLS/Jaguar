import time
import json
from enum import Enum

from engine.l3_os.tools import Tool, ToolArg


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



class MockChoice(Enum):
    choiceOne = 'choiceOne'
    choiceTwo = 'choiceTwo'


class Plant:
    pass


class ToolArgMethods:
    @staticmethod
    def valid_type_func(this : str, other : int):
        print(f'this, other = {this}, {other}')

    @staticmethod
    def invalid_type_func(plant : Plant):
        pass

    @staticmethod
    def enum_type_func(choice : MockChoice):
        print(f'I decided on {choice}')

    @staticmethod
    def default_val_func(num : int = 200):
        print(f'The number is {num}')

    @staticmethod
    def unannotated(num, the_str):
        pass

    @staticmethod
    def no_args_func():
        print(f'Hello world')

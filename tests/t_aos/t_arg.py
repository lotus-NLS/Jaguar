from enum import Enum

from engine.l3_aos.tools import ToolArg
from holytools.devtools import Unittest, ModuleInspector

# ----------------------------------------------------------

class TestToolArgGeneration(Unittest):
    def test_basic_nonoptional(self):
        tool_args = []
        for arg in ModuleInspector.get_args(func=ToolArgMethods.valid_type_func):
            tool_args.append(ToolArg.from_function_arg(arg=arg))
            self.assertTrue(not arg.has_default_val())
        for tool_arg in tool_args:
            self.assertTrue(tool_arg.dtype in [str, int])
            self.assertTrue(not tool_arg.is_optional)
            print(f'tool arg dtype is {tool_arg.dtype}')

    def test_basic_optional(self):
        tool_args = []
        for arg in ModuleInspector.get_args(func=ToolArgMethods.default_val_func):
            tool_args.append(ToolArg.from_function_arg(arg=arg))
            self.assertTrue(arg.has_default_val())
            print(f'Argument default val is {arg.get_default_val()}')
        for tool_arg in tool_args:
            self.assertTrue(tool_arg.is_optional)

    def test_enum_arg(self):
        tool_args = []
        for arg in ModuleInspector.get_args(func=ToolArgMethods.enum_type_func):
            tool_arg = ToolArg.from_function_arg(arg=arg)
            tool_args.append(tool_arg)
            print(f'arg dtype is {arg.dtype}')
            self.assertTrue(issubclass(arg.dtype, Enum))
            print(f'tool arg choices are {tool_arg.choices}')
            self.assertTrue(tool_arg.choices == [choice.value for choice in MockChoice])

    def test_unannotated_args(self):
            with self.assertRaises(ValueError):
                ModuleInspector.get_args(func=ToolArgMethods.unannotated)

    def test_no_args(self):
        args = ModuleInspector.get_args(func=ToolArgMethods.no_args_func)
        self.assertTrue(len(args) == 0)


class MockChoice(Enum):
    choiceOne = 'choiceOne'
    choiceTwo = 'choiceTwo'


class ToolArgMethods:
    @staticmethod
    def valid_type_func(this : str, other : int):
        print(f'this, other = {this}, {other}')

    @staticmethod
    def default_val_func(num : int = 200):
        print(f'The number is {num}')

    @staticmethod
    def enum_type_func(choice : MockChoice):
        print(f'I decided on {choice}')

    @staticmethod
    def unannotated(num, the_str):
        pass

    @staticmethod
    def no_args_func():
        print(f'Hello world')


if __name__ == "__main__":
    TestToolArgGeneration.execute_all()




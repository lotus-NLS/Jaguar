from enum import Enum

from holytools.devtools import Unittest, ModuleInspector

from engine.l4_tools import ToolArg
from tests.spoofs import ToolArgMethods, MockChoice


class TestToolArg(Unittest):
    def setUp(self):
        self.tool_arg_methods = ToolArgMethods()

    def test_valid_args(self):
        tool_args = []
        for arg in ModuleInspector.get_args(func=self.tool_arg_methods.valid_type_func):
            tool_args.append(ToolArg.from_function_arg(arg=arg))
            self.assertTrue(not arg.has_default_val())
        for tool_arg in tool_args:
            self.assertTrue(tool_arg.dtype in [str, int])
            self.assertTrue(not tool_arg.is_optional)
            print(f'tool arg dtype is {tool_arg.dtype}')


    def test_default_val(self):
        tool_args = []
        for arg in ModuleInspector.get_args(func=self.tool_arg_methods.default_val_func):
            tool_args.append(ToolArg.from_function_arg(arg=arg))
            self.assertTrue(arg.has_default_val())
            print(f'Argument default val is {arg.get_default_val()}')
        for tool_arg in tool_args:
            self.assertTrue(tool_arg.is_optional)


    def test_enum_func(self):
        tool_args = []
        for arg in ModuleInspector.get_args(func=self.tool_arg_methods.enum_type_func):
            tool_arg = ToolArg.from_function_arg(arg=arg)
            tool_args.append(tool_arg)
            print(f'arg dtype is {arg.dtype}')
            self.assertTrue(issubclass(arg.dtype, Enum))
            print(f'tool arg choices are {tool_arg.choices}')
            self.assertTrue(tool_arg.choices == [choice.value for choice in MockChoice])


    def test_invalid_args(self):
            with self.assertRaises(ValueError):
                ModuleInspector.get_args(func=self.tool_arg_methods.unannotated)

    def test_no_args(self):
        args = ModuleInspector.get_args(func=self.tool_arg_methods.no_args_func)
        self.assertTrue(len(args) == 0)


if __name__ == "__main__":
    TestToolArg.execute_all()
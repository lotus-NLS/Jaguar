from engine.l3_aos.tools import ToolArg
from holytools.devtools import Unittest, ModuleInspector

# ----------------------------------------------------------

class TestToolArg(Unittest):
    def test_from_valid(self):
        tool_args = []
        for arg in ModuleInspector.get_args(func=ToolArgMethods.valid_type_func):
            tool_args.append(ToolArg.from_function_arg(arg=arg))
            self.assertTrue(not arg.has_default_val())
        for tool_arg in tool_args:
            self.assertTrue(tool_arg.dtype in [str, int])
            self.assertTrue(not tool_arg.is_optional)
            print(f'tool arg dtype is {tool_arg.dtype}')

        tool_args = []
        for arg in ModuleInspector.get_args(func=ToolArgMethods.default_val_func):
            tool_args.append(ToolArg.from_function_arg(arg=arg))
            self.assertTrue(arg.has_default_val())
            print(f'Argument default val is {arg.get_default_val()}')
        for tool_arg in tool_args:
            self.assertTrue(tool_arg.is_optional)

        args = ModuleInspector.get_args(func=ToolArgMethods.no_args_func)
        self.assertTrue(len(args) == 0)

    def test_from_invalid(self):
        with self.assertRaises(ValueError):
            ModuleInspector.get_args(func=ToolArgMethods.unannotated)

    def test_get_value(self):
        test_values = ['test', '100', '1', None]
        test_dtypes = [str, int, bool, str]

        for dtype, val in zip(test_dtypes, test_values):
            ta = ToolArg(name=f'Test{dtype}',dtype=dtype)
            ta.input = val
            if ta.input is None:
                self.assertTrue(ta.get_value() is None)
            else:
                self.assertIsInstance(ta.get_value(), dtype)


class ToolArgMethods:
    @staticmethod
    def valid_type_func(this : str, other : int):
        print(f'this, other = {this}, {other}')

    @staticmethod
    def default_val_func(num : int = 200):
        print(f'The number is {num}')

    @staticmethod
    def unannotated(num, the_str):
        pass

    @staticmethod
    def no_args_func():
        print(f'Hello world')


if __name__ == "__main__":
    TestToolArg.execute_all()




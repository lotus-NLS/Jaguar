from enum import Enum

from engine.l3_aos.tools import ToolArg, ToolCall
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

    def test_invalid_dtype(self):
        with self.assertRaises(TypeError):
            ToolArg(name='Test', dtype=Enum)

class TestToolCall(Unittest):
    def test_update(self):
        js1 = '{"arg_one": "value"}'
        js2 = ',{"arg_two": "value"}'
        n1, n2 = 'Hammer', 'Screwdriver'

        tool_call = ToolCall(name=n1, args_json=js1)
        other = ToolCall(name=n2, args_json=js2)
        tool_call.update(other)
        self.assertTrue(tool_call.name == n1+n2)
        self.assertTrue(tool_call.args_json == js1 + js2)

    def test_get_args(self):
        tool_call = ToolCall(name='Hammer', args_json='{"arg_one": "value"}')
        args_dict= tool_call.get_args_dict()
        self.assertTrue(len(args_dict) == 1)
        for k, v in args_dict.items():
            self.assertTrue(k == 'arg_one')
            self.assertTrue(v == 'value')

    def test_non_string_items(self):
        tc1 = ToolCall(name='Hammer', args_json='{"arg_one": 1}')
        tc2 = ToolCall(name='Screwdriver', args_json='{"arg_one": "1"}')

        arg_dict_one = tc1.get_args_dict()
        arg_dict_two = tc2.get_args_dict()
        for (v1,v2) in zip(arg_dict_one.values(), arg_dict_two.values()):
            print(v1, v2)
            print(type(v1), type(v2))
            self.assertTrue(type(v1) == type(v2))

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
    TestToolCall.execute_all()

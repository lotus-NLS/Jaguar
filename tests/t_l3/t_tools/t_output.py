from engine.l3_aos.tools.output import ExitStatus, MissingArgs
from tests.t_l3.t_tools.tooltest import ToolTest


class TestToolOutput(ToolTest):
    def test_output_value(self):
        output = self.simple_tool.execute(self.valid_tool_call.get_args_dict())
        self.assertIn("value", output.value)

    def test_success(self):
        output = self.simple_tool.execute(self.valid_tool_call.get_args_dict())
        report = output.get_report()
        self.assertIn(self.simple_tool.get_name(), report)
        self.assertIn(ExitStatus.SUCCESS.value, report)

    def test_exception_reported(self):
        output = self.invalid_tool.execute(self.valid_tool_call.get_args_dict())
        report = output.get_report()
        error_msgs = output.get_error_msgs()
        self.assertIn(self.invalid_tool.get_name(), report)
        self.assertIn(ExitStatus.EXCEPTION.value, report)
        self.assertTrue(any(msg for msg in error_msgs))

    def test_error_messages(self):
        output = self.simple_tool.execute(self.invalid_tool_call.get_args_dict())
        error_msgs = output.get_error_msgs()
        print(f'- Error messages: {error_msgs}')
        self.assertTrue(any(f'{MissingArgs.__name__}' in msg for msg in error_msgs))


if __name__ == "__main__":
    TestToolOutput.execute_all()
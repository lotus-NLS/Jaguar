from engine.l3_aos.tools import ToolOutput
from engine.l3_aos.tools.output import ExitStatus, MissingArgs, ProgressUpdate
from tests.t_l3.t_tools.tooltest import BaseTest


# -----------------------------------------------------

class TestExitStatus(BaseTest):
    def test_success(self):
        output = self.simple_tool.handle(self.valid_tool_call)
        self.assertIsInstance(output, ToolOutput)
        self.assertEqual(output.get_exit_status(), ExitStatus.SUCCESS)

    def test_timeout(self):
        self.simple_tool.timeout = 0.000
        output = self.simple_tool.handle(self.valid_tool_call)
        self.assertEqual(output.get_exit_status(), ExitStatus.FAILED)

    def test_exception(self):
        output = self.invalid_tool.handle(self.valid_tool_call)
        self.assertEqual(output.get_exit_status(), ExitStatus.EXCEPTION)
        self.assertTrue(any(msg.progress_type == ProgressUpdate.EXCEPTION for msg in output.progress_msgs))

    def test_missing_required_arg(self):
        output = self.simple_tool.handle(self.empty_tool_call)
        self.assertEqual(output.get_exit_status(), ExitStatus.FAILED)
        self.assertTrue(any(msg.progress_type == ProgressUpdate.FAILED for msg in output.progress_msgs))

    def test_invalid_arg(self):
        output = self.simple_tool.handle(self.invalid_tool_call)
        self.assertEqual(output.get_exit_status(), ExitStatus.FAILED)


class TestToolOutput(BaseTest):
    def test_output_value(self):
        output = self.simple_tool.handle(self.valid_tool_call)
        self.assertIn("value", output.value)

    def test_success(self):
        output = self.simple_tool.handle(self.valid_tool_call)
        report = output.get_report()
        self.assertIn(self.simple_tool.get_name(), report)
        self.assertIn(ExitStatus.SUCCESS.value, report)

    def test_exception_reported(self):
        output = self.invalid_tool.handle(self.valid_tool_call)
        report = output.get_report()
        error_msgs = output.get_error_msgs()
        self.assertIn(self.invalid_tool.get_name(), report)
        self.assertIn(ExitStatus.EXCEPTION.value, report)
        self.assertTrue(any(msg for msg in error_msgs))

    def test_error_messages(self):
        output = self.simple_tool.handle(self.invalid_tool_call)
        error_msgs = output.get_error_msgs()
        self.assertTrue(any(f'{MissingArgs.__name__}' in msg for msg in error_msgs))


if __name__ == "__main__":
    TestToolOutput.execute_all()
    TestExitStatus.execute_all()

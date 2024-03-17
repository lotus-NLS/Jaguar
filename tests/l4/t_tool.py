from engine.l4_tools import ToolCall
from engine.l4_tools.tool_output import MissingArgs, ExitStatus, Progress, ToolOutput
from hollarek.devtools import Unittest
from tests.spoofs import SpoofPrinter, SpoofErrorRaiser, SpoofToolCall


class ToolTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.valid_tool_call = ToolCall(json_str=SpoofToolCall.valid_printer_args)
        cls.invalid_tool_call = ToolCall(json_str=SpoofToolCall.invalid_printer_args)
        cls.empty_tool_call = ToolCall(json_str=SpoofToolCall.empty_args_json)

    def setUp(self):
        self.simple_tool = SpoofPrinter()
        self.invalid_tool = SpoofErrorRaiser()


class TestExitStatus(ToolTest):
    def test_success(self):
        output = self.simple_tool.handle(self.valid_tool_call)
        self.assertIsInstance(output, ToolOutput)
        self.assertEqual(output.exit_status, ExitStatus.SUCCESS)

    def test_timeout(self):
        self.simple_tool.timeout = 0.000
        output = self.simple_tool.handle(self.valid_tool_call)
        self.assertEqual(output.exit_status, ExitStatus.FAILED)

    def test_exception(self):
        output = self.invalid_tool.handle(self.valid_tool_call)
        self.assertEqual(output.exit_status, ExitStatus.EXCEPTION)
        self.assertTrue(any(msg.progress_type == Progress.EXCEPTION for msg in output.progress))

    def test_missing_required_arg(self):
        output = self.simple_tool.handle(self.empty_tool_call)
        self.assertEqual(output.exit_status, ExitStatus.FAILED)
        self.assertTrue(any(msg.progress_type == Progress.FAILED for msg in output.progress))

    def test_invalid_arg(self):
        output = self.simple_tool.handle(self.invalid_tool_call)
        self.assertEqual(output.exit_status, ExitStatus.FAILED)


class TestToolOutput(ToolTest):
    def test_output_value(self):
        output = self.simple_tool.handle(self.valid_tool_call)
        self.assertIn("value", output.value)

    def test_report_success(self):
        output = self.simple_tool.handle(self.valid_tool_call)
        report = output.get_report()
        self.assertIn(SpoofPrinter.get_name(), report)
        self.assertIn("Exit status: SUCCESS", report)

    def test_report_exception(self):
        output = self.invalid_tool.handle(self.valid_tool_call)
        report = output.get_report()
        error_msgs = output.get_error_msgs()
        self.assertIn(SpoofErrorRaiser.get_name(), report)
        self.assertIn("EXCEPTION", report)
        self.assertTrue(any(msg for msg in error_msgs))

    def test_error_messages(self):
        output = self.simple_tool.handle(self.invalid_tool_call)
        error_msgs = output.get_error_msgs()
        self.assertTrue(any(f'{MissingArgs.__name__}' in msg for msg in error_msgs))

if __name__ == "__main__":
    TestToolOutput.execute_all()
    TestExitStatus.execute_all()

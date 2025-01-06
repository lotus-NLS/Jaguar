# from engine.l3_os.tools import ToolOutput
# from engine.l3_os.tools.tool_output import ExitStatus, Progress, MissingArgs
# from tests.l3.tooltest import BaseTest
#
#
# # -----------------------------------------------------
#
# class TestExitStatus(BaseTest):
#     def test_success(self):
#         output = self.simple_tool.handle(self.valid_tool_call)
#         self.assertIsInstance(output, ToolOutput)
#         self.assertEqual(output.exit_status, ExitStatus.SUCCESS)
#
#     def test_timeout(self):
#         self.simple_tool.timeout = 0.000
#         output = self.simple_tool.handle(self.valid_tool_call)
#         self.assertEqual(output.exit_status, ExitStatus.FAILED)
#
#     def test_exception(self):
#         output = self.invalid_tool.handle(self.valid_tool_call)
#         self.assertEqual(output.exit_status, ExitStatus.EXCEPTION)
#         self.assertTrue(any(msg.progress_type == Progress.EXCEPTION for msg in output.progress))
#
#     def test_missing_required_arg(self):
#         output = self.simple_tool.handle(self.empty_tool_call)
#         self.assertEqual(output.exit_status, ExitStatus.FAILED)
#         self.assertTrue(any(msg.progress_type == Progress.FAILED for msg in output.progress))
#
#     def test_invalid_arg(self):
#         output = self.simple_tool.handle(self.invalid_tool_call)
#         self.assertEqual(output.exit_status, ExitStatus.FAILED)
#
#
# class TestToolOutput(BaseTest):
#     def test_output_value(self):
#         output = self.simple_tool.handle(self.valid_tool_call)
#         self.assertIn("value", output.value)
#
#     def test_report_success(self):
#         output = self.simple_tool.handle(self.valid_tool_call)
#         report = output.get_report()
#         self.assertIn(self.simple_tool.get_name(), report)
#         self.assertIn(ExitStatus.SUCCESS.value, report)
#
#     def test_report_exception(self):
#         output = self.invalid_tool.handle(self.valid_tool_call)
#         report = output.get_report()
#         error_msgs = output.get_error_msgs()
#         self.assertIn(self.invalid_tool.get_name(), report)
#         self.assertIn(ExitStatus.EXCEPTION.value, report)
#         self.assertTrue(any(msg for msg in error_msgs))
#
#     def test_error_messages(self):
#         output = self.simple_tool.handle(self.invalid_tool_call)
#         error_msgs = output.get_error_msgs()
#         self.assertTrue(any(f'{MissingArgs.__name__}' in msg for msg in error_msgs))
#
#
# if __name__ == "__main__":
#     TestToolOutput.execute_all()
#     TestExitStatus.execute_all()

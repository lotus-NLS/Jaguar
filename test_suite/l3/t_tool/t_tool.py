import time
from hollarek.devtools import Unittest
from engine.l3_applications.tool.input import ToolCall
from engine.l3_applications.tool.tool import Tool
from engine.l3_applications.tool.input import ToolArg
from engine.l3_applications.tool.output import ToolOutput, ExitStatus, Progress
import json

class SimpleTool(Tool):
    def __init__(self, call_timeout: float = 60):
        super().__init__(call_timeout=call_timeout)
        self.text_arg : ToolArg = ToolArg(name="arg_one")
        self.text_arg_two : ToolArg = ToolArg(name="arg_two", is_optional=True)

    def do(self):
        time.sleep(0.1)
        msg = f"SimpleTool says: {self.text_arg.val}"
        print(msg)
        return msg

    def get_desc(self) -> str:
        return "SimpleTool is a basic implementation for testing."


class InvalidTool(Tool):
    def get_desc(self) -> str:
        return 'throws error on execution'

    def do(self):
        raise ValueError


class ToolTest(Unittest):
    @classmethod
    def setUpClass(cls):
        pass  # Implement if needed for class-wide setup

    def setUp(self):
        self.simple_tool = SimpleTool()
        self.invalid_tool = InvalidTool()
        self.valid_args_json = json.dumps({f'{self.simple_tool.text_arg.name}': 'value'})
        self.invalid_args_json = json.dumps({'arg_onee': ''})
        self.empty_args_json = json.dumps({})


class TestExitStatus(ToolTest):
    def test_success(self):
        tool_call = ToolCall(json_str=self.valid_args_json)
        output = self.simple_tool.handle(tool_call)
        self.assertIsInstance(output, ToolOutput, "Output should be a ToolOutput instance.")
        self.assertEqual(output.exit_status, ExitStatus.SUCCESS, "Tool should execute successfully.")

    def test_timeout(self):
        self.simple_tool.timeout = 0.000
        tool_call = ToolCall(json_str=self.valid_args_json)
        output = self.simple_tool.handle(tool_call)
        self.assertEqual(output.exit_status, ExitStatus.FAILED, "Tool should fail due to timeout.")

    def test_exception(self):
        tool = InvalidTool()
        tool_call = ToolCall(json_str=self.valid_args_json)
        output = tool.handle(tool_call)
        self.assertEqual(output.exit_status, ExitStatus.EXCPETION, "Tool should fail due to exception.")
        self.assertTrue(any(msg.progress_type == Progress.EXCEPTION for msg in output.progress), "Output should contain exception message.")

    def test_missing_required_arg(self):
        tool_call = ToolCall(json_str=self.empty_args_json)
        output = self.simple_tool.handle(tool_call)
        self.assertEqual(output.exit_status, ExitStatus.FAILED, "Tool should fail due to missing arguments.")
        self.assertTrue(any(msg.progress_type == Progress.FAILED for msg in output.progress), "Output should contain failure message.")

    def test_invalid_arg(self):
        tool_call = ToolCall(json_str=self.invalid_args_json)
        output = self.simple_tool.handle(tool_call)
        self.assertEqual(output.exit_status, ExitStatus.FAILED, "Tool should fail due to invalid argument value.")


class TestToolOutput(ToolTest):
    def test_output_value(self):
        tool_call = ToolCall(json_str=self.valid_args_json)
        output = self.simple_tool.handle(tool_call)
        fail_msg = f"Should be value; is {output.value}"
        self.assertIn("value",output.value, fail_msg)

    def test_report_success(self):
        tool_call = ToolCall(json_str=self.valid_args_json)
        output = self.simple_tool.handle(tool_call)
        report = output.get_report()
        self.assertIn("SimpleTool", report, f"Report is {report}, should contain \"SimpleTool\"")
        self.assertIn("Exit status: SUCCESS", report, "Report for SimpleTool should indicate success.")


    def test_report_exception(self):
        tool_call = ToolCall(json_str=self.valid_args_json)
        output = self.invalid_tool.handle(tool_call)
        report = output.get_report()
        error_msgs = output.get_error_msgs()
        self.assertIn("InvalidTool", report, "Report should include the tool name for InvalidTool.")
        self.assertIn("EXCEPTION", report, "Report for InvalidTool should indicate failure.")
        self.assertTrue(any(msg for msg in error_msgs), "Error message should be included in error messages for InvalidTool.")


    def test_error_messages(self):
        tool_call = ToolCall(json_str=self.invalid_args_json)
        output = self.simple_tool.handle(tool_call)
        print(f'report : {output.get_report()}')

        error_msgs = output.get_error_msgs()

        msg = f"Error messages is {error_msgs}, should contain \"Invalid argument\""
        print(msg)
        self.assertTrue(any("Missing Arguments" in msg for msg in error_msgs), msg)



if __name__ == "__main__":
    TestToolOutput.execute_all()
    TestExitStatus.execute_all()

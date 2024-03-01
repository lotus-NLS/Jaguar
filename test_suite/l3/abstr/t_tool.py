import time
import traceback

from hollarek.dev.test import Unittest
from engine.l3_applications.tool.input import ToolCall
from engine.l3_applications.tool.tool import Tool
from engine.l3_applications.tool.input import ToolArg
from engine.l3_applications.tool.output import ToolOutput, ExitStatus, Progress
import json



class SimpleTool(Tool):
    def __init__(self, call_timeout: float = 60):
        super().__init__(call_timeout=call_timeout)
        self.text_arg : ToolArg = ToolArg(name="arg_one")

    def do(self):
        time.sleep(0.1)
        msg = f"SimpleTool says: {self.text_arg.val}"
        print(msg)
        return msg

    def get_desc(self) -> str:
        return "SimpleTool is a basic implementation for testing."

    def get_args(self) -> list[ToolArg]:
        return [self.text_arg]



class TestExitStatus(Unittest):
    @classmethod
    def setUpClass(cls):
        pass  # Implement if needed for class-wide setup

    def setUp(self):
        self.simple_tool = SimpleTool()
        self.valid_args_json = json.dumps({f'{self.simple_tool.text_arg.name}': 'value'})
        self.invalid_args_json = json.dumps({'arg_onee': ''})
        self.empty_args_json = json.dumps({})

    def test_tool_name(self):
        try:
            self.assertEqual(self.simple_tool.get_name(), self.simple_tool.__name__, "Tool name should be 'SimpleTool'.")
        except Exception as e:
            print(e)

    def test_desc(self):
        description = self.simple_tool.get_desc()
        self.assertIsInstance(description, str, "Description should be a string.")
        self.assertNotEqual(description, "", "Description should not be empty.")


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

    def test_missing_args(self):
        tool_call = ToolCall(json_str=self.empty_args_json)
        output = self.simple_tool.handle(tool_call)
        self.assertEqual(output.exit_status, ExitStatus.FAILED, "Tool should fail due to missing arguments.")
        self.assertTrue(any(msg.update_type == Progress.FAILED for msg in output.progress), "Output should contain failure message.")

    def test_invalid_arg(self):
        tool_call = ToolCall(json_str=self.invalid_args_json)
        output = self.simple_tool.handle(tool_call)
        self.assertEqual(output.exit_status, ExitStatus.FAILED, "Tool should fail due to invalid argument value.")


# class TestOutput(Unittest):



if __name__ == "__main__":
    TestExitStatus.execute_all()
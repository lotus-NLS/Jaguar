from engine.l3_aos.tools import ToolOutput, ToolDoc
from engine.l3_aos.tools.output import ExitStatus, ProgUpdate
from tests.t_l3.t_tools.tooltest import ToolTest


# -----------------------------------------------------

class TestTool(ToolTest):
    def setUp(self):
        super().setUp()
        self.EXCEPTION = ProgUpdate.exception(content='')
        self.FAILED = ProgUpdate.failed(content='')

    def test_success(self):
        output = self.simple_tool.execute(self.valid_tool_call.get_args_dict())
        self.assertIsInstance(output, ToolOutput)
        self.assertEqual(output.get_exit_status(), ExitStatus.SUCCESS)

    def test_timeout(self):
        self.simple_tool.timeout = 0.000
        output = self.simple_tool.execute(self.valid_tool_call.get_args_dict())
        self.assertEqual(output.get_exit_status(), ExitStatus.FAILED)

    def test_exception(self):
        output = self.invalid_tool.execute(self.valid_tool_call.get_args_dict())
        self.assertEqual(output.get_exit_status(), ExitStatus.EXCEPTION)
        self.assertTrue(any(msg.update_type == self.EXCEPTION.update_type for msg in output.prog_updates))

    def test_missing_required_arg(self):
        output = self.simple_tool.execute(self.empty_tool_call.get_args_dict())
        self.assertEqual(output.get_exit_status(), ExitStatus.FAILED)
        self.assertTrue(any(msg.update_type == self.FAILED.update_type for msg in output.prog_updates))

    def test_invalid_arg(self):
        output = self.simple_tool.execute(self.invalid_tool_call.get_args_dict())
        self.assertEqual(output.get_exit_status(), ExitStatus.FAILED)


class TestToolDoc(ToolTest):
    def test_properties(self):
        doc = self.simple_tool.get_doc()
        doc.get_desc()

    def test_from_info(self):
        actual_name, actual_desc, actual_args = 'TestName', 'TestDescription', self.simple_tool.get_args()
        doc = ToolDoc.from_info(name=actual_name, desc=actual_desc, args=actual_args)
        name, desc, args = doc.get_tool_name(), doc.get_desc(), doc.get_parameters()

        self.assertTrue(name == actual_name)
        self.assertTrue(desc == actual_desc)
        self.assertTrue(len(args) == len(actual_args))

        for a in args:
            args[a]['type'] = 'string'
            args[a]['description'] = ''

        print(f'Tool documentation view')
        print(doc.get_view())


if __name__ == "__main__":
    TestToolDoc.execute_all()
    TestTool.execute_all()

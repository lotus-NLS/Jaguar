from engine.l4_tools import ToolDoc, ToolCall
from engine.l2_os import Application, Action
from tests.spoofs import MockWorkspace, InvalidArgWorkspace
from hollarek.devtools import Unittest

# ---------------------------------------------------------

class ApplicationTest(Unittest):
    def setUp(self):
        self.app = Application(index=0, workspace_type=MockWorkspace, desc='Test application')


class TestOpenClose(ApplicationTest):
    def test_basic_properties(self):
        self.assertEqual(self.app.get_name(), 'Application')
        self.assertIsInstance(self.app.desc, str)
        self.assertFalse(self.app.is_open())

    def test_open_application(self):
        self.app.open(uri='some_path')
        self.assertTrue(self.app.is_open())
        self.assertIsInstance(self.app.window.tab_map[0], MockWorkspace)

    def test_close_application(self):
        self.app.open(uri='some_path')
        self.app.close()
        self.assertFalse(self.app.is_open())
        self.assertTrue(len(self.app.window.get_tabs()) == 0)

    def test_close_individual_tabs(self):
        self.app.open(uri='tab1')
        self.app.open(uri='tab2')
        initial_tab_count = len(self.app.window.tab_map)
        self.app.window.close_tab(0)
        self.assertEqual(len(self.app.window.tab_map), initial_tab_count - 1)


class TestActionProperties(ApplicationTest):
    def test_action_generation(self):
        self.app.open(uri='some_path')
        for text in ['add', 'reset']:
            contains_keyword = any([text in action.get_name() for action in self.app.get_actions()])
            self.assertTrue(contains_keyword)

    def test_action_docs(self):
        actions = self.app.get_actions()
        for action in actions:
            self.assertIsInstance(action.get_doc(), ToolDoc)

    def test_action_type(self):
        actions = self.app.get_actions()
        for action in actions:
            self.assertIsInstance(action, Action)

    def test_num_actions(self):
        self.app.open(uri='test_path')
        actions = self.app.get_actions()
        actions_info = [action.get_name() for action in actions]
        self.log(f'Actions are : {actions_info}')
        self.assertEqual(2, len(actions))

    def test_invalid_args(self):
        with self.assertRaises(TypeError):
            invalid_arg_app = Application(index=1, workspace_type=InvalidArgWorkspace, desc='Invalid arg application')


class TestActionExecution(ApplicationTest):
    def test_tool_execution(self):
        self.app.open(uri='test_path')
        add = self.app.tool_dict['add']
        reset = self.app.tool_dict['reset']

        add_json_str = '{"msg": "New text", "tab_index" : "0"}'
        tool_call = ToolCall(json_str=add_json_str)

        add.handle(tool_call=tool_call)
        self.assertIn('New text', self.app.window.tab_map[0].get_text())
        self.log(f'Window context before reset: {self.app.window.get_entry()}')

        reset_json_str = '{"tab_index" : "0"}'
        tool_call = ToolCall(json_str=reset_json_str)
        reset.handle(tool_call)
        self.assertEqual('', self.app.window.tab_map[0].get_text())
        self.log(f'Window context after reset : {self.app.window.get_entry()}')


if __name__ == '__main__':
    # TestApplicationOpenClose.execute_all()
    # TestActionProperties.execute_all()
    TestActionProperties.execute_all()
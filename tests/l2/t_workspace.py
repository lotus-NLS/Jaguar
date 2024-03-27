from engine.l4_tools import ToolDoc, ToolCall
from engine.l2_os import Action
from tests.spoofs import MockWorkspace
from hollarek.devtools import Unittest

# ---------------------------------------------------------

class WorkspaceTest(Unittest):
    def setUp(self):
        self.workspace = MockWorkspace()


class TestWorkspaceOpenClose(WorkspaceTest):
    def test_basic_properties(self):
        self.assertIsInstance(self.workspace.get_desc(), str)
        self.assertFalse(self.workspace.is_active)

    def test_open_application(self):
        self.workspace.open_action.do()
        self.assertTrue(self.workspace.is_active)
        self.assertIsInstance(self.workspace, MockWorkspace)

    def test_close_application(self):
        self.workspace.open_action.do()
        self.workspace.close_action.do()
        self.assertFalse(self.workspace.is_active)


class TestWorkspaceActions(WorkspaceTest):
    def test_action_generation(self):
        self.workspace.open_action.do()
        action_names = [action.get_name() for action in self.workspace.get_actions()]
        print(f'Action names are: {action_names}')
        for text in ['add', 'reset']:
            contains_keyword = any([text in action.get_name() for action in self.workspace.get_actions()])
            self.assertTrue(contains_keyword)

    def test_action_docs(self):
        actions = self.workspace.get_actions()
        for action in actions:
            self.assertIsInstance(action.get_doc(), ToolDoc)

    def test_action_type(self):
        actions = self.workspace.get_actions()
        for action in actions:
            self.assertIsInstance(action, Action)

    def test_num_actions(self):
        self.workspace.open_action.do()
        actions = self.workspace.get_actions()
        actions_info = [action.get_name() for action in actions]
        self.log(f'Actions are : {actions_info}')
        self.assertEqual(3, len(actions))


class TestActionExecution(WorkspaceTest):
    def test_tool_execution(self):
        self.workspace.open_action.do()
        actions = self.workspace.get_actions()
        actions_map : dict[str, Action] = {action.get_name() : action for action in actions}

        add, reset = None, None
        for key, value in actions_map.items():
            print(key)
            if 'add' in key:
                add = value
            if 'reset' in key:
                reset = value
        if add is None or reset is None:
            raise ValueError('Add or reset action not found')


        add_json_str = '{"msg": "New text"}'
        tool_call = ToolCall(json_str=add_json_str)

        add.handle(tool_call=tool_call)
        self.assertIn('New text', self.workspace.get_text())
        self.log(f'Window context before reset: {self.workspace.get_entry()}')

        reset_json_str = '{}'
        tool_call = ToolCall(json_str=reset_json_str)
        reset.handle(tool_call)
        self.assertEqual('', self.workspace.get_text())
        self.log(f'Window context after reset : {self.workspace.get_entry()}')


if __name__ == '__main__':
    # TestWorkspaceOpenClose.execute_all()
    TestWorkspaceActions.execute_all()
    # TestActionExecution.execute_all()
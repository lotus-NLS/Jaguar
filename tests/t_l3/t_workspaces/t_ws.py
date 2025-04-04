from typing import Optional

from engine.l2_models.language import Message
from engine.l3_aos.tools import ToolDoc, ToolCall, Tool
from engine.l3_aos.workspaces import Workspace
from holytools.devtools import Unittest
from PIL.Image import Image as PILImage

# ---------------------------------------------------------

class TestWorkspace(Unittest):
    def setUp(self):
        self.workspace = MockWorkspace()

    def test_tool_execution(self):
        self.workspace.open_action._do()
        actions = self.workspace.get_actions()
        actions_map : dict[str, Tool] = {action.get_name() : action for action in actions}

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

        add.execute(args_dict=tool_call.get_args_dict())
        self.assertIn('New text', self.workspace.get_text())
        self.log(f'Window context before reset: {Message.from_workspace(ws=self.workspace)}')

        reset_json_str = '{}'
        tool_call = ToolCall(json_str=reset_json_str)
        reset.execute(args_dict=tool_call.get_args_dict())
        self.assertEqual('', self.workspace.get_text())
        self.log(f'Window context after reset : {Message.from_workspace(ws=self.workspace)}')


    def test_toggle_active_inactive(self):
        print(f'Workspace active = {self.workspace.is_active}')
        self.assertFalse(self.workspace.is_active)
        self.workspace.open_action._do()
        print(f'Workspace active after open actio = {self.workspace.is_active}')
        self.assertTrue(self.workspace.is_active)
        self.workspace.close_action._do()
        print(f'Workspace active after close actio = {self.workspace.is_active}')
        self.assertFalse(self.workspace.is_active)


    def test_get_actions(self):
        while_open_actions = ['add', 'reset', 'close']
        while_closed_actions = ['open']

        action_names = [action.get_name() for action in self.workspace.get_actions()]
        print(f'Actions while open = {action_names}')
        for keyword in while_open_actions:
            contains_keyword = any([keyword in name for name in action_names])
            self.assertFalse(contains_keyword)
        for keyword in while_closed_actions:
            contains_keyword = any([keyword in name for name in action_names])
            self.assertTrue(contains_keyword)

        self.workspace.open_action._do()
        action_names = [action.get_name() for action in self.workspace.get_actions()]
        print(f'Actions while open = {action_names}')
        for keyword in while_open_actions:
            contains_keyword = any([keyword in name for name in action_names])
            self.assertTrue(contains_keyword)
        for keyword in while_closed_actions:
            contains_keyword = any([keyword in name for name in action_names])
            self.assertFalse(contains_keyword)


    def test_get_actiondocs(self):
        actions_docs = self.workspace.get_action_docs()
        for docs in actions_docs:
            self.assertIsInstance(docs, ToolDoc)


class MockWorkspace(Workspace):
    def __init__(self):
        super().__init__()
        self.text_content = 'Initial'

    def open(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    def get_text(self) -> str:
            return self.text_content

    def get_image(self) -> Optional[PILImage]:
        return None

    def add(self, msg: str):
        self.text_content += ' ' + msg

    def reset(self):
        self.text_content = ''


if __name__ == '__main__':
    TestWorkspace.execute_all()

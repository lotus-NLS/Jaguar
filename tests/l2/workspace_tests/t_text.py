from hollarek.file import File, FileSpoofer
from hollarek.devtools import Unittest
from engine.l2_os import DocumentEditor
from engine.l4_tools import ToolCall
import json

# ---------------------------------------------------------

class TestTextWorkspace(Unittest):
    def setUp(self):
        self.test_text : File = FileSpoofer.lend_txt()
        self.workspace = DocumentEditor()
        tool_call = ToolCall(json_str= json.dumps({'filepath' : self.test_text.fpath}))
        self.workspace.open_action.handle(tool_call)
        print(f'Test text file fpath : {self.test_text.fpath}')

    def test_content(self):
        self.log(msg=f'Initial content: \n{self.workspace.get_text()}')

    def test_insert(self):
        new_content = 'Second line \n'
        self.workspace.insert(2, new_content)
        self.assertIn(new_content, self.workspace.get_text())
        self.log(msg=f'After inserting \"{new_content.__repr__()}\": \n{self.workspace.get_text()}')

    def test_delete_lines(self):
        del_lines = (1,1)
        self.workspace.delete_lines(*del_lines)
        with open(self.test_text.fpath, 'r') as f:
            content = f.readlines()
        self.assertEqual(len(content), 1)
        self.log(f'After deleting lines {del_lines}: \n{self.workspace.get_text()}')



if __name__ == '__main__':
    TestTextWorkspace.execute_all()

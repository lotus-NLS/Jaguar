from hollarek.file import File, FileSpoofer
from engine.l2_os import LotusText
from hollarek.devtools import Unittest

# ---------------------------------------------------------

class TestTextWorkspace(Unittest):
    def setUp(self):
        self.test_text : File = FileSpoofer.lend_txt()

    def test_content(self):
        workspace = LotusText()
        self.log(msg=f'Initial content: \n{workspace.get_text()}')

    def test_insert(self):
        workspace = LotusText()
        new_content = 'Second line \n'
        workspace.insert(2, new_content)
        self.assertIn(new_content, workspace.get_text())
        self.log(msg=workspace.get_text())

    def test_delete_lines(self):
        workspace = LotusText()
        workspace.delete_lines(1, 1)
        with open(self.test_text.fpath, 'r') as f:
            content = f.readlines()
        self.assertEqual(len(content), 1)
        self.log(f'After deleting: \n{workspace.get_text()}')



if __name__ == '__main__':
    TestTextWorkspace.execute_all()

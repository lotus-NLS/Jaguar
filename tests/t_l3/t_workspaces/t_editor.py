from engine.l3_aos import PythonIDE
import tempfile

from holytools.devtools import Unittest
from holytools.fsys import Directory, FsysManager

import os

# --------------------------------------------------------------


class PythonTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.proj_dirpath : str = tempfile.mktemp()
        os.makedirs(cls.proj_dirpath)
        cls.ide : PythonIDE = PythonIDE()
        cls.ide.open(project_dirpath=cls.proj_dirpath)
        cls.view = cls.ide.view

    def setUp(self):
        self.script_fpath = os.path.join(self.proj_dirpath, 'test.py')
        with open(self.script_fpath, 'w') as f:
            testscript_content = "print(f'Hello world :)')\na = 2\nb=3"
            f.write(testscript_content)


class TestProjectView(PythonTest):
    def test_open_file(self):
        self.ide.open_file(fileNo=0)
        self.ide.get_text()

        self.ide.open_file(fileNo=1)

    def test_script_display(self):
        file_content = self.ide.view._get_file_with_lineno(fpath=self.script_fpath)
        excepted_content = ''' 1   | print(f'Hello world :)')
 2   | a = 2
 3   | b=3'''

        print(f'- Initial file content:\n{file_content}')
        print(f'- Expected file content:\n{excepted_content}')
        self.assertEqual(file_content, excepted_content)

    def test_exclude_directores(self):
        manager = FsysManager(root_dirpath=self.proj_dirpath)
        manager.add_tree(tree={'.venv': {}, '__pycache__' : {}, 'somefile.txt' : 'Content'})

        filetree = self.view.get_project_filetree()
        print(f'- Filetree:\n{filetree}')
        self.assertTrue(not '.venv' in filetree)
        self.assertTrue(not '__pycache__' in filetree)
        self.assertTrue('somefile.txt' in filetree)
        self.assertTrue('test.py' in filetree)

    def test_get_described_tree(self):
        description_map = {os.path.join(self.root_dirpath, 'file1.txt') : 'This is a file'}
        tree = self.root_node.get_tree(desc_map=description_map)
        print(f'- Described tree:\n{tree}')
        self.assertTrue(f'🗎 file1.txt\n			This is a file' in tree)

    def test_enumerated_tree(self):
        path_to_fileID = {os.path.join(self.root_dirpath, 'file1.txt') : '1'}

        tree = self.root_node.get_tree(path_to_fileID=path_to_fileID)
        print(f'- Enumerated tree:\n{tree}')
        self.assertTrue(f'🗎 file1.txt | FileID = 1' in tree)


if __name__ == "__main__":
    TestDecoratedDirectory.execute_all()
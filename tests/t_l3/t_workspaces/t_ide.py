import os
import tempfile

from engine.l3_aos import PythonIDE
from engine.l3_aos.workspaces.python_editor import PythonEditor
from holytools.devtools import Unittest
from holytools.fsys import FsysManager


# --------------------------------------------------------------


class PythonTest(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.proj_dirpath : str = tempfile.mktemp()
        os.makedirs(cls.proj_dirpath)
        cls.ide : PythonIDE = PythonIDE()
        cls.ide.open(project_dirpath=cls.proj_dirpath)

    def setUp(self):
        self.script_fpath = os.path.join(self.proj_dirpath, 'test.py')
        with open(self.script_fpath, 'w') as f:
            testscript_content = "print(f'Hello world :)')\na = 2\nb=3"
            f.write(testscript_content)
        manager = FsysManager(root_dirpath=self.proj_dirpath)
        manager.add_tree(tree={'.venv': {}, '__pycache__' : {}, 'somefile.txt' : 'Content'})


class TestIDE(PythonTest):
    def test_open_file(self):
        self.ide.open_file(projectFileNo=0)
        file_content = PythonEditor._get_file_with_lineno(fpath=self.script_fpath)
        excepted_content = ''' 1   | print(f'Hello world :)')
    2   | a = 2
    3   | b=3'''

        print(f'- Initial file content:\n{file_content}')
        print(f'- Expected file content:\n{excepted_content}')
        self.assertEqual(file_content, excepted_content)

        text = self.ide.get_text()
        print(f'- Text:\n{text}')
        self.assertTrue('🗎 test.py | FileID = 0' in text)

    def test_run_file(self):
        self.ide.run_file(openFileNo=0)
        out1 = self.ide.output_map[self.script_fpath]
        print(f'- Run output:\n{out1}')
        self.assertTrue('Hello world :)' in out1)

        self.ide.run_file(openFileNo=0)
        out2 = self.ide.output_map[self.script_fpath]
        print(f'- Run output:\n{out2}')
        self.assertTrue('Hello world :)' in out2)

    def test_insert(self):
        self.ide.open_file(projectFileNo=0)
        fpath = self.script_fpath
        new_content = f'import PIL\n'
        self.ide.insert(fileNo=0, after_line=0, content=new_content)

        file_content = PythonEditor._get_file_with_lineno(fpath=fpath)
        expected_file_content = ''' 1   | import PIL
 2   | 
 3   | print(f'Hello world :)')
 4   | a = 2
 5   | b=3'''
        print(f'- New file content:\n{file_content}')
        print(f'- Expected file content\n{expected_file_content}')
        self.assertEqual(file_content, expected_file_content)

    def test_replace(self):
        self.ide.open_file(projectFileNo=0)
        fpath = self.script_fpath
        self.ide.replace(fileNo=0, start_line=1, end_line=1, content='')

        file_content = PythonEditor._get_file_with_lineno(fpath=fpath)
        expected_file_content = ''' 1   | a = 2
 2   | b=3'''

        print(f'- New file content:\n{file_content}')
        print(f'- Expected content:\n{expected_file_content}')

        self.assertEqual(file_content, expected_file_content)

    def test_venv_exists(self):
        self.assertTrue(not self.ide.interpreter_fpath is None)
        self.assertTrue(os.path.isfile(self.ide.interpreter_fpath))


class TestProjectNode(PythonTest):
    def test_exclude_directores(self):
        self.ide._populate_project(desc_map={}, path_to_fileID={})
        filetree = self.ide._get_project_filetree()

        print(f'- Filetree:\n{filetree}')
        self.assertTrue(not '.venv' in filetree)
        self.assertTrue(not '__pycache__' in filetree)
        self.assertTrue('somefile.txt' in filetree)
        self.assertTrue('test.py' in filetree)

    def test_describe_dirs(self):
        description_map = {os.path.join(self.proj_dirpath, 'somefile.txt') : 'This is a file'}

        self.ide._populate_project(desc_map=description_map, path_to_fileID={})
        tree = self.ide._get_project_filetree()
        print(f'- Described tree:\n{tree}')
        self.assertTrue(f'🗎 somefile.txt\n\tThis is a file' in tree)

    def test_enumerated_tree(self):
        path_to_fileID = {os.path.join(self.proj_dirpath, 'somefile.txt') : '1'}

        self.ide._populate_project(desc_map={}, path_to_fileID=path_to_fileID)
        tree = self.ide._get_project_filetree()
        print(f'- Enumerated tree:\n{tree}')
        self.assertTrue(f'🗎 somefile.txt | FileID = 1' in tree)


if __name__ == "__main__":
    TestIDE.execute_all()
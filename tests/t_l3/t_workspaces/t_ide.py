import os
import tempfile

from engine.l3_aos.workspaces.python_ide import PythonIDE
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
        cls.view = cls.ide.view

    def setUp(self):
        self.script_fpath = os.path.join(self.proj_dirpath, 'test.py')
        with open(self.script_fpath, 'w') as f:
            testscript_content = "print(f'Hello world :)')\na = 2\nb=3"
            f.write(testscript_content)


class TestPythonIDE(PythonTest):
    def test_insert(self):
        self.ide.open_file(fpath=self.script_fpath)
        fpath = self.script_fpath
        new_content = f'import PIL\n'
        self.ide.insert(fileNo=0, after_line=0, content=new_content)

        file_content = self.ide.view._get_with_lineno(fpath=fpath)
        expected_file_content = ''' 1   | import PIL
 2   | 
 3   | print(f'Hello world :)')
 4   | a = 2
 5   | b=3'''
        print(f'- New file content:\n{file_content}')
        print(f'- Expected file content\n{expected_file_content}')
        self.assertEqual(file_content, expected_file_content)

    def test_replace(self):
        self.ide.open_file(fpath=self.script_fpath)
        fpath = self.script_fpath
        self.ide.replace(fileNo=0, start_line=1, end_line=1, content='')

        file_content = self.ide.view._get_with_lineno(fpath=fpath)
        expected_file_content = ''' 1   | a = 2
 2   | b=3'''

        print(f'- New file content:\n{file_content}')
        print(f'- Expected content:\n{expected_file_content}')

        self.assertEqual(file_content, expected_file_content)

    def test_run_file(self):
        self.ide.run_file(script_fpath=self.script_fpath)
        out1 = self.ide.output_map[self.script_fpath]
        print(f'- Run output:\n{out1}')
        self.assertTrue('Hello world :)' in out1)

        relative_script_fpath = os.path.relpath(self.script_fpath, start=self.ide.proj_dirpath)
        self.ide.run_file(script_fpath=relative_script_fpath)
        out2 = self.ide.output_map[self.script_fpath]
        print(f'- Run output:\n{out2}')
        self.assertTrue('Hello world :)' in out2)

    def test_venv_exists(self):
        self.assertTrue(not self.ide.interpreter_fpath is None)
        self.assertTrue(os.path.isfile(self.ide.interpreter_fpath))


class TestProjectView(PythonTest):
    def test_open_file(self):
        self.ide.open_file(fpath='newfile.py')
        self.ide.get_text()

        fpath = 'test.py'
        self.ide.open_file(fpath=fpath)

    def test_script_display(self):
        file_content = self.ide.view._get_with_lineno(fpath=self.script_fpath)
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

if __name__ == "__main__":
    TestPythonIDE.execute_all()
    TestProjectView.execute_all()
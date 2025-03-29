import os
import tempfile

from engine.l3_aos.workspaces.python_ide import PythonProject
from holytools.devtools import Unittest

# --------------------------------------------------------------

class TestPythonIDE(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.tempdir : str = tempfile.mktemp()
        os.makedirs(cls.tempdir)
        cls.project : PythonProject = PythonProject(project_dirpath=cls.tempdir)
        cls.project.mkvenv()

    def setUp(self):
        self.script_fpath = os.path.join(self.tempdir, 'test.py')
        with open(self.script_fpath, 'w') as f:
            testscript_content = "print(f'Hello world :)')\na = 2\nb=3"
            f.write(testscript_content)

    def test_open_new(self):
        self.project.open_file(fpath='newfile.py')
        self.project.get_view()

    def test_relative_fpath(self):
        fpath = 'test.py'
        self.project.open_file(fpath=fpath)

    def test_script_display(self):
        file_content = self.project._view_with_lineno(fpath=self.script_fpath)
        expected_file_content = ''' 1   | print(f'Hello world :)')
 2   | a = 2
 3   | b=3'''

        print(f'- Initial file content:\n{file_content}')
        self.assertEqual(file_content, expected_file_content)


    def test_run_file(self):
        self.project.run_file(script_fpath=self.script_fpath)
        print(f'- Run output:\n{self.project.run_output}')
        self.assertTrue('Hello world :)' in self.project.run_output)

    def test_venv_exists(self):
        self.assertTrue(not self.project.interpreter_fpath is None)
        self.assertTrue(os.path.isfile(self.project.interpreter_fpath))

    def test_write(self):
        self.project.open_file(fpath=self.script_fpath)
        fpath = self.script_fpath
        new_content = f'import PIL\n'
        self.project.write(fileNo=0, after_line=0, content=new_content)

        file_content = self.project._view_with_lineno(fpath=fpath)
        expected_file_content = ''' 1   | import PIL
 2   | 
 3   | print(f'Hello world :)')
 4   | a = 2
 5   | b=3'''

        print(f'- New file content:\n{file_content}')
        self.assertEqual(file_content, expected_file_content)

    def test_delete(self):
        self.project.open_file(fpath=self.script_fpath)
        fpath = self.script_fpath
        self.project.delete(fileNo=0, start_line=1, end_line=1)

        file_content = self.project._view_with_lineno(fpath=fpath)
        expected_file_content = ''' 1   | a = 2
 2   | b=3'''

        print(f'- New file content:\n{file_content}')
        self.assertEqual(file_content, expected_file_content)

if __name__ == "__main__":
    TestPythonIDE.execute_all()
import os
import tempfile

from engine.l3_aos.workspaces.python_ide import PythonProject
from holytools.devtools import Unittest

# --------------------------------------------------------------

class TestPythonIDE(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.tempdir : str = tempfile.mktemp()
        cls.project : PythonProject = PythonProject(project_dirpath=cls.tempdir)
        cls.project.mkvenv()

        this_dir = os.path.dirname(__file__)
        cls.script_fpath = os.path.join(this_dir, 'testscript.py')

    def test_script_display(self):
        file_content = self.project.get_with_lineno(fpath=self.script_fpath)
        expected_content = ''' 1   | import os
 2   | import sys
 3   | 
 4   | print(sys.path)
 5   | print(os.getcwd())
 6   | 
 7   | import PIL.Image as Image
 8   | from engine.l3_aos.aos import AOS
 9   | _, __ = Image, AOS(workspaces=[])
 10  | 
 11  | print('Hello world!')
 12  | raise Exception(f'fuck you')
 13  | 
 14  | '''
        self.assertEqual(file_content, expected_content)

    def test_run_file(self):
        self.project.run_file(script_fpath=self.script_fpath)
        self.assertTrue(len(self.project.run_output) > 0)

    def test_venv_exists(self):
        self.assertTrue(not self.project.interpreter_fpath is None)
        self.assertTrue(os.path.isfile(self.project.interpreter_fpath))


if __name__ == "__main__":
    TestPythonIDE.execute_all()
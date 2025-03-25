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

        this_dir = os.path.dirname(__file__)
        cls.script_fpath = os.path.join(this_dir, 'testscript.py')

    def test_script_display(self):
        file_content = self.project._get_with_lineno(fpath=self.script_fpath)
        expected_line = 'from engine.l3_aos.aos import AOS'
        self.assertTrue(expected_line in file_content)

    def test_run_file(self):
        self.project.run_file(script_fpath=self.script_fpath)
        print(f'- Run output:\n{self.project.run_output}')
        self.assertTrue('Hello world :)' in self.project.run_output)

    def test_venv_exists(self):
        self.assertTrue(not self.project.interpreter_fpath is None)
        self.assertTrue(os.path.isfile(self.project.interpreter_fpath))



if __name__ == "__main__":
    TestPythonIDE.execute_all()
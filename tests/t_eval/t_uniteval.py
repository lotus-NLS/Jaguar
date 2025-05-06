import os

from eval.task.dirt.evals import TerminalEval
from holytools.devtools import Unittest
from holytools.fsys import Directory


class TestEvaluation(Unittest):

    def test_project_copy(self):
        te = TerminalEval.ready()

        proj_dirpath = te.proj_dirpath
        calc_fpath = os.path.join(proj_dirpath, 'calculator.py')

        self.assertTrue(os.path.isdir(te.proj_dirpath))
        self.assertTrue(os.path.isfile(calc_fpath))

        proj_directory = Directory(path=proj_dirpath)
        print(proj_directory.get_tree())

if __name__ == "__main__":
    TestEvaluation.execute_all()
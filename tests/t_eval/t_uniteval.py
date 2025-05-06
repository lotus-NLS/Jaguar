import os

from eval.task.evals import TerminalEval, BrowserEval, PythonEval
from holytools.devtools import Unittest
from holytools.fsys import Directory


class TestEvaluation(Unittest):

    def test_project_copy(self):
        te, be, pe = TerminalEval.ready(), BrowserEval.ready(), PythonEval.ready()
        for ev in [te, be, pe]:
            proj_dirpath = ev.proj_dirpath
            calc_fpath = os.path.join(proj_dirpath, 'calculator.py')

            self.assertTrue(os.path.isdir(ev.proj_dirpath))
            self.assertTrue(os.path.isfile(calc_fpath))

            proj_directory = Directory(path=proj_dirpath)
            print(proj_directory.get_tree())


if __name__ == "__main__":
    TestEvaluation.execute_all()
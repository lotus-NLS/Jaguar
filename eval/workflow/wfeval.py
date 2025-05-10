import os.path
import subprocess
import sys

from eval.uniteval import UnitEval
from holytools.devtools import Unittest


class WorkflowEval(UnitEval):
    def evaluate_unittest(self, unittest : type[Unittest]):
        cls_fpath = sys.modules[unittest.__module__].__file__
        cls_fname = os.path.basename(cls_fpath)

        testenv_script_fpath = os.path.join(self.frame_dirpath,cls_fname)
        print(f'-Script dirpath = {testenv_script_fpath}')
        process = subprocess.Popen([self.testenv_python_fpath, f'{testenv_script_fpath}'])
        exit_code = process.wait()
        
        return exit_code == 0


if __name__ == '__main__':
    pass
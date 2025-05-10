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

        input(f'Implement the solution if you please!'
              f'Module can be found at {os.path.join(self.proj_dirpath, 'build.py')}')

        env = os.environ.copy()
        env['PYTHONPATH'] = f'{self.testenv_dirpath}'
        print(env['PYTHONPATH'])
        process = subprocess.Popen(['/home/daniel/lotus/engine/.venv/bin/python', f'{testenv_script_fpath}'], env=env)
        exit_code = process.wait()

        return exit_code == 0


if __name__ == '__main__':
    pass
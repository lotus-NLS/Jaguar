import os
import shutil
import subprocess
import sys
import tempfile
from typing import Optional

import fuzzywuzzy.fuzz
import fuzzywuzzy.fuzz

from engine.l0_main.lotus_engine import LotusEngine
from holytools.devtools import Unittest
from holytools.logging import CaptureLogs

# ---------------------------------------------------

class UnitEval(Unittest):
    @classmethod
    def setUpClass(cls):
        cls.engine : LotusEngine = LotusEngine()

    def setUp(self):
        self.engine.reset()
        cls_dirpath = os.path.dirname(sys.modules[self.__class__.__module__].__file__)

        source_proj_dirpath = os.path.join(cls_dirpath, 'project')
        source_frame_dirpath = os.path.join(cls_dirpath, 'frame')
        source_venv_dirpath = self.get_cachedvenv_dirpath()

        self.testenv_dirpath = tempfile.mktemp()
        self.proj_dirpath = os.path.join(self.testenv_dirpath, 'project')
        self.frame_dirpath = os.path.join(self.testenv_dirpath, 'frame')
        self.testenv_venv_dirpath = os.path.join(self.testenv_dirpath, '.venv')
        self.testenv_python_fpath = os.path.join(self.testenv_venv_dirpath, 'bin', 'python')

        shutil.copytree(source_proj_dirpath, self.proj_dirpath)
        shutil.copytree(source_frame_dirpath, self.frame_dirpath)
        shutil.copytree(source_venv_dirpath, self.testenv_venv_dirpath)

        print(f'- Set up test environment at "{self.testenv_dirpath}"')

    @classmethod
    def evaluate(cls, reps : int = 5, test_names : Optional[list[str]] = None):
        log_capture = CaptureLogs()

        with log_capture:
            ut = cls.ready()
            ut.execute_stats(reps=reps, min_success_percent=100, test_names=test_names)

        module = sys.modules[cls.__module__]
        script_dirpath = os.path.dirname(module.__file__)
        log_fpath = os.path.join(script_dirpath, f'{cls.__name__}.txt')
        with open(log_fpath, 'a') as f:
            f.write(log_capture.get_stored())

    @staticmethod
    def values_match(v1: str, v2: str, fuzzy : bool, fuzzy_tol : int = 75):
        if '|' in v2:
            v21, v22 = v2.split('||')
            v21_match = UnitEval.values_match(v1, v21, fuzzy=fuzzy, fuzzy_tol=fuzzy_tol)
            v22_match = UnitEval.values_match(v1, v22, fuzzy=fuzzy, fuzzy_tol=fuzzy_tol)
            return v21_match or v22_match

        if fuzzy:
            match = fuzzywuzzy.fuzz.ratio(v1, v2) > fuzzy_tol
        else:
            match = v1 == v2
        return match

    @staticmethod
    def get_cachedvenv_dirpath() -> str:
        cache_dirpath = os.path.expanduser('~/.cache/uniteval')
        os.makedirs(cache_dirpath, exist_ok=True)

        venv_dirpath = os.path.join(cache_dirpath, '.venv')
        python_dirpath = os.path.join(venv_dirpath, 'bin', 'python')
        env = {'PATH' : os.environ['PATH']}
        if not os.path.isdir(venv_dirpath):
            subprocess.run(['python3', '-m', 'venv', venv_dirpath], env=env)
            subprocess.run([python_dirpath, '-m', 'pip', 'install', 'holytools'], env=env)

        return venv_dirpath


if __name__ == "__main__":
    UnitEval.ready()
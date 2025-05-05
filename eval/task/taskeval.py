import os
from typing import Optional
from eval.uniteval import Uniteval
from holytools.logging import CaptureLogs


class TaskEval(Uniteval):
    @classmethod
    def evaluate(cls, reps : int = 5, test_names : Optional[list[str]] = None):
        log_capture = CaptureLogs()

        with log_capture:
            tt = cls.ready()
            tt.execute_stats(reps=reps, min_success_percent=100, test_names=test_names)

        script_dirpath = os.path.dirname(__file__)
        log_dirpath = os.path.join(script_dirpath, 'logs')
        log_fpath = os.path.join(log_dirpath, f'{cls.__name__}.txt')

        os.makedirs(log_dirpath, exist_ok=True)
        with open(log_fpath, 'a') as f:
            f.write(log_capture.get_stored())
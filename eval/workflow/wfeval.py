import os
from typing import Optional
from eval.uniteval import Uniteval


class WFEval(Uniteval):
    @classmethod
    def log_fpath(cls) -> Optional[str]:
        script_dirpath = os.path.dirname(__file__)
        cls_name = cls.__name__
        log_dirpath = os.path.join(script_dirpath, 'logs')
        os.makedirs(log_dirpath, exist_ok=True)

        return os.path.join(log_dirpath, f'{cls_name}.txt')

import os
import inspect
from typing import Optional

def get_function_args(func: callable) -> list[str]:
    func_sig = inspect.signature(func)
    params = list(func_sig.parameters.keys())
    return params


def get_parentfile_path() -> Optional[str]:
    try:
        frame = inspect.currentframe().f_back.f_back
        filename = frame.f_globals["__file__"]
        rootpath = os.path.abspath(filename)
    except:
        rootpath = None
    return rootpath
import os

from engine.l3_aos.workspaces.python_ide import PythonIDE
from eval.zcenarios.python import listdir, calculator


class BasicProject:
    def __init__(self, proj_dirpath : str = '/tmp/1213a3cd-7fd4-4fb0-8e3e-0c4f544d4db0'):
        self.proj_dirpath : str = proj_dirpath
        if not os.path.isdir(self.proj_dirpath):
            os.makedirs(self.proj_dirpath)
            PythonIDE._mkvenv(proj_dirpath=self.proj_dirpath)

        calc_fpath = calculator.__file__
        listdir_fpath = listdir.__file__

        self.copy_file(source_fpath=calc_fpath, dest_fpath=os.path.join(self.proj_dirpath, 'calculator.py'))
        self.copy_file(source_fpath=listdir_fpath, dest_fpath=os.path.join(self.proj_dirpath, 'listdir.py'))

    @staticmethod
    def copy_file(source_fpath: str, dest_fpath: str):
        with open(source_fpath, 'rb') as f:
            content = f.read()
            with open(dest_fpath, 'wb') as f2:
                f2.write(content)
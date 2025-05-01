import os
import subprocess
import tempfile

from eval.cenarios.python import listdir, calculator


class BasicProject:
    def __init__(self):
        self.proj_dirpath : str = tempfile.mkdtemp()
        subprocess.run(['python3', '-m', 'venv', f'{self.proj_dirpath}/.venv'])
        self.reset_files()

    def reset_files(self):
        calc_fpath = calculator.__file__
        listdir_fpath = listdir.__file__

        self.copy_file(source_fpath=calc_fpath, dest_fpath=os.path.join(self.proj_dirpath, 'calculator.py'))
        self.copy_file(source_fpath=listdir_fpath, dest_fpath=os.path.join(self.proj_dirpath, 'listdir.py'))
        self.copy_file(source_fpath=__file__, dest_fpath=os.path.join(self.proj_dirpath, 'api_retrieval.py'))

    @staticmethod
    def copy_file(source_fpath: str, dest_fpath: str):
        with open(source_fpath, 'rb') as f:
            content = f.read()
            with open(dest_fpath, 'wb') as f2:
                f2.write(content)
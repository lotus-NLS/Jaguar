import os
import subprocess
import tempfile

from eval.task.scenarios.python import calculator, listdir, api_retrieval


class BasicPythonProject:
    def __init__(self):
        self.proj_dirpath : str = tempfile.mkdtemp()
        subprocess.run(['python3', '-m', 'venv', f'{self.proj_dirpath}/.venv'])
        self.reset_files()

    def reset_files(self):
        calc_fpath = calculator.__file__
        listdir_fpath = listdir.__file__
        retrieval_fpath = api_retrieval.__file__

        self.copy_file(source_fpath=calc_fpath, dest_dirpath=self.proj_dirpath)
        self.copy_file(source_fpath=listdir_fpath, dest_dirpath=self.proj_dirpath)
        self.copy_file(source_fpath=retrieval_fpath, dest_dirpath=self.proj_dirpath)

    @staticmethod
    def copy_file(source_fpath: str, dest_dirpath : str):
        fname = os.path.basename(source_fpath)
        dest_fpath = os.path.join(dest_dirpath, fname)

        with open(source_fpath, 'rb') as f:
            content = f.read()
            with open(dest_fpath, 'wb') as f2:
                f2.write(content)
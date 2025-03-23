import os
from typing import Optional

from PIL.Image import Image as PILImage
import subprocess
from engine.l3_aos import Workspace
from holytools.fsys import FsysNode
import re

# --------------------------------------------

class PythonIDE(Workspace):
    def __init__(self):
        super().__init__()
        self.project : Optional[PythonProject] = None

    def open(self, project_dirpath : str):
        self.project = PythonProject(project_dirpath=project_dirpath)

    def close(self, *args, **kwargs):
        self.project = None

    def switch_project(self, workspace_dirpath : str):
        self.project = PythonProject(project_dirpath=workspace_dirpath)

    def run_file(self, script_dirpath : str):
        self.project.run_file(script_dirpath=script_dirpath)

    def get_text(self) -> str:
        return self.project.get_text()

    def get_image(self) -> Optional[PILImage]:
        return None


class PythonProject:
    def __init__(self, project_dirpath : str):
        self.dirpath : str = project_dirpath
        if not self.dirpath:
            raise ValueError(f'Project dirpath does not exist: {self.dirpath}')
        venv_python_fpath = os.path.join(self.dirpath, '.venv/bin/python')
        self.interpreter_fpath : Optional[str] = venv_python_fpath if os.path.isfile(venv_python_fpath) else None
        self.excluded_dirs : list[str] = ['.venv', '.git', '.idea']
        self.excluded_patterns : list[str] = ['.*\\.pyc']
        self.run_output : Optional[str] = None
        self.open_fpaths : list[str] = []

    def get_text(self) -> str:
        pass

    def mkvenv(self):
        pass

    def run_file(self, script_dirpath : str):
        script_path = '/home/daniel/testdir/srcdir/newfile.py'
        result = subprocess.run([self.interpreter_fpath, script_path], capture_output=True, text=True)
        self.run_output = f'{result.stdout}\n{result.stderr}\nExit code: {result.returncode}'

    def get_project_filetree(self):
        root_node = FsysNode(path=self.dirpath)
        fpaths = root_node.get_subfile_paths()
        fpaths = [p for p in fpaths if not self.is_excluded(fpath=p)]

        return '\n'.join(fpaths)

    def is_excluded(self, fpath : str) -> bool:
        excluded_paths = [os.path.join(self.dirpath, name) for name in self.excluded_dirs]
        in_excluded = any([fpath.startswith(excluded_path) for excluded_path in excluded_paths])

        excluded_reg_patterns = [re.compile(pattern) for pattern in self.excluded_patterns]
        matches_exclusion_pattern = any([pattern.match(fpath) for pattern in excluded_reg_patterns])

        return in_excluded or matches_exclusion_pattern

if __name__ == "__main__":
    project = PythonProject(project_dirpath=f'/home/daniel/lotus/engine')
    print(project.get_project_filetree())
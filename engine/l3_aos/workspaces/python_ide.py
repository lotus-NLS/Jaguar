import os
from typing import Optional

from PIL.Image import Image as PILImage
import subprocess
from engine.l3_aos import Workspace
import re

from holytools.fsys import Directory


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

    def run_file(self, script_fpath : str):
        self.project.run_file(script_fpath=script_fpath)

    def open_file(self, fpath : str):
        self.project.open_file(fpath=fpath)

    def close_file(self, fpath : str):
        self.project.close_file(fpath=fpath)

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

    def mkvenv(self):
        pass

    def open_file(self, fpath : str):
        self.open_fpaths.append(fpath)

    def close_file(self, fpath : str):
        self.open_fpaths.remove(fpath)

    def run_file(self, script_fpath : str):
        result = subprocess.run([self.interpreter_fpath, script_fpath], capture_output=True, text=True)
        header = f'{script_fpath}\n'
        script_stdout = f'{result.stdout}'
        script_stderr = f'\033[31m{result.stderr}\033[0m'
        exit_code_msg = f'Exit code: {result.returncode}'

        self.run_output = f'{script_fpath}\n{script_stdout}{script_stderr}\n{exit_code_msg}'

    def get_text(self) -> str:
        text = f'+--- Project metadata ---+\n{self.get_metadata()}\n\n'
        text += f'+--- Project structure: ---+\n{self.get_project_filetree()}\n'
        if self.open_fpaths:
            text += f'+--- Open files ---+\n{self.get_file_contents()}\n'
        if self.run_output:
            text += f'+--- Execution output ---+\n{self.run_output}'

        return text

    # -----------------------------------------------

    def get_metadata(self) -> str:
        venv = os.path.relpath(self.interpreter_fpath, self.dirpath) if self.interpreter_fpath else None
        metadata = (f'{"Project name":<20}: {os.path.basename(self.dirpath)}\n'
                    f'{"Project dirpath":<20}: {self.dirpath} \n'
                    f'{"Virtual environment":<20}: {venv}')
        return metadata

    def get_project_filetree(self):
        root_node = Directory(path=self.dirpath)
        fpaths = root_node.get_subfile_fpaths()
        fpaths = [p for p in fpaths if not self._is_excluded(fpath=p)]
        fpaths = [os.path.relpath(p, self.dirpath) for p in fpaths]

        fs_dict = root_node.to_dict(fpaths=fpaths)
        filetree = root_node.dict_to_tree(fs_dict=fs_dict, max_children=10)

        return filetree

    def _is_excluded(self, fpath : str) -> bool:
        excluded_paths = [os.path.join(self.dirpath, name) for name in self.excluded_dirs]
        in_excluded = any([fpath.startswith(excluded_path) for excluded_path in excluded_paths])

        excluded_reg_patterns = [re.compile(pattern) for pattern in self.excluded_patterns]
        matches_exclusion_pattern = any([pattern.match(fpath) for pattern in excluded_reg_patterns])

        return in_excluded or matches_exclusion_pattern

    def get_file_contents(self) -> str:
        all_contents = ''
        for path in self.open_fpaths:
            all_contents += self.get_with_lineno(fpath=path)
        return all_contents

    @staticmethod
    def get_with_lineno(fpath : str):
        with open(fpath, 'r') as f:
            c = f.read()
        lines = c.split('\n')

        enumerated_content = ''
        for n, l in enumerate(lines):
            enumerated_content += f'{n+1:< 5}| {l}\n'
        return enumerated_content.rstrip('\n')


if __name__ == "__main__":
    test_dirpath = f'/home/daniel/lotus/engine'
    testscript_fpath = os.path.join(test_dirpath, 'tests/t_l3/t_workspaces/testscript.py')

    project = PythonProject(project_dirpath=test_dirpath)
    # print(project.get_project_filetree())
    # print(project.get_metadata())
    # print(project.get_with_lineno(fpath=script_fpath))
    print(project.get_text())
    project.run_file(script_fpath=testscript_fpath)
    print(project.run_output)
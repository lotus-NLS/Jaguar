import os
import shutil
import subprocess
from typing import Optional

from PIL.Image import Image as PILImage
from engine.l3_aos.workspaces.python_editor import PythonProject
from engine.l3_aos.workspaces.workspace import Workspace

# --------------------------------------------

class PythonIDE(Workspace):
    """LotusPythonIDE: Minimal text operable python IDE"""
    def __init__(self):
        super().__init__()
        self.proj_dirpath : Optional[str] = None
        self.interpreter_fpath : Optional[str] = None
        self.editor : Optional[PythonProject] = None

        self.output_map : dict[str, str] = {}
        self._open_fpaths : list[str] = []

    # -------------------------------------------------------
    # Workspace generics

    def open(self, project_dirpath : str):
        """Starts a minimal text operable python IDE only available to you. Use for python development tasks."""
        project_dirpath = self._get_abspath(fpath=project_dirpath)
        if not os.path.isdir(project_dirpath):
            raise ValueError(f'Project dirpath does not exist: {project_dirpath}')

        cache_venv_dirpath = self._get_cachedvenv_dirpath()
        proj_venv_dirpath = os.path.join(project_dirpath, '.venv')
        shutil.copytree(cache_venv_dirpath, proj_venv_dirpath)
        self.proj_dirpath = project_dirpath
        self.editor = PythonProject(proj_dirpath=project_dirpath, interpreter_fpath=self.interpreter_fpath)
        self.interpreter_fpath = os.path.join(proj_venv_dirpath, 'bin/python')


    def close(self, *args, **kwargs):
        self.editor = None

    def get_text(self) -> str:
        return self.editor.get_view(open_fpaths=self._open_fpaths, run_output=self.output_map)

    def get_image(self) -> Optional[PILImage]:
        return None

    # --------------------------------------------------------------------
    # Functionalities

    def run_file(self, script_fpath : str):
        script_fpath = self._get_abspath(fpath=script_fpath)
        env, cwd = {'PYTHONPATH': self.proj_dirpath}, self.proj_dirpath
        arg_list = [self.interpreter_fpath, script_fpath]
        result = subprocess.run(arg_list, capture_output=True, text=True, env=env, cwd=cwd)

        script_stdout = f'{result.stdout}'
        script_stderr = f'\033[31m{result.stderr}\033[0m'
        exit_code_msg = f'Process finished with exit code {result.returncode}'

        self.output_map[script_fpath] = f'{script_fpath}\n{script_stdout}{script_stderr}\n{exit_code_msg}'

    def open_file(self, fpath : str):
        """Opens a file specified relative to the project dirpath. If the file does not exist it is created instead"""
        fpath = self._get_abspath(fpath=fpath)
        parent_dir = os.path.dirname(fpath)

        if not os.path.isdir(parent_dir):
            raise ValueError(f'Parent directory of file does not exist: {parent_dir}')
        if not os.path.isfile(fpath):
            with open(fpath, 'w') as f:
                f.write('')
        self._open_fpaths.append(fpath)
        
    def close_file(self, fpath : str):
        """Closes file spcified relative to the project dirpath"""
        fpath = self._get_abspath(fpath=fpath)
        self._open_fpaths.remove(fpath)

    def replace(self, fileNo : int, start_line : int, end_line : int, content : str):
        """Replaces lines starting from [line_start] to [line_end] including start and end in fileNo [fileNo] with new [content]"""
        self.editor.replace(fpath=self._open_fpaths[fileNo], line_start=start_line, line_end=end_line, content=content)

    def insert(self, fileNo : int, after_line : int, content : str):
        """Inserts [content] at line [line] in fileNo [fileNo]"""
        self.editor.insert(fpath=self._open_fpaths[fileNo], after_line=after_line, content=content)

    def _get_abspath(self, fpath : str):
        fpath= os.path.expanduser(fpath)
        if os.path.isabs(fpath):
            return fpath
        else:
            return os.path.join(self.proj_dirpath, fpath)

    @staticmethod
    def _get_cachedvenv_dirpath() -> str:
        cache_dirpath = os.path.expanduser('~/.cache/jaguar')
        os.makedirs(cache_dirpath, exist_ok=True)

        venv_dirpath = os.path.join(cache_dirpath, '.venv')
        env = {'PATH' : os.environ['PATH']}
        if not os.path.isdir(venv_dirpath):
            subprocess.run(['python3', '-m', 'venv', venv_dirpath], env=env)
        return venv_dirpath





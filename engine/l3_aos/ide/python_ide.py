import os
import shutil
import subprocess
from typing import Optional

from PIL.Image import Image as PILImage

from engine.l3_aos.ide.node import ModuleNode
from engine.l3_aos.ide.python_editor import PythonEditor
from engine.l3_aos.workspace import Workspace
from holytools.userIO import MessageFormatter


# --------------------------------------------

class PythonIDE(Workspace):
    """LotusPythonIDE: Minimal text operable python IDE"""
    def __init__(self):
        super().__init__()
        self.proj_dirpath : Optional[str] = None
        self.interpreter_fpath : Optional[str] = None

        self.root_node : Optional[ModuleNode] = None
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
        self.interpreter_fpath = os.path.join(proj_venv_dirpath, 'bin/python')
        self.root_node = ModuleNode(path=project_dirpath)
        self.root_node.fill_ancestors(desc_map={})

    def close(self, *args, **kwargs):
        pass

    @staticmethod
    def _get_cachedvenv_dirpath() -> str:
        cache_dirpath = os.path.expanduser('~/.cache/jaguar')
        os.makedirs(cache_dirpath, exist_ok=True)

        venv_dirpath = os.path.join(cache_dirpath, '.venv')
        env = {'PATH' : os.environ['PATH']}
        if not os.path.isdir(venv_dirpath):
            subprocess.run(['python3', '-m', 'venv', venv_dirpath], env=env)
        return venv_dirpath

    def get_text(self) -> str:
        self.root_node.fill_ancestors(desc_map={})
        proj_info = PythonEditor.get_info(proj_dirpath=self.proj_dirpath, venv_dirpath=self.interpreter_fpath)
        filetree = self.root_node.get_tree(show_idx=True)
        editor = PythonEditor.get_editor(open_fpaths=self._open_fpaths, run_output=self.output_map)

        view = MessageFormatter.get_boxed(text=proj_info, headline=f'Project metadata')
        view += MessageFormatter.get_boxed(text=filetree, headline=f'Project file structure ({self.proj_dirpath})')
        if self._open_fpaths:
            view += editor
        return view

    def get_image(self) -> Optional[PILImage]:
        return None

    # --------------------------------------------------------------------
    # Functionalities

    def open_file(self, projectFileNo : int):
        """Opens a file specified relative to the project dirpath. If the file does not exist it is created instead"""
        idx = int(projectFileNo)
        fpath= self.root_node.get_path(idx=idx)
        parent_dir = os.path.dirname(fpath)

        if not os.path.isdir(parent_dir):
            raise ValueError(f'Parent directory of file does not exist: {parent_dir}')
        if not os.path.isfile(fpath):
            with open(fpath, 'w') as f:
                f.write('')
        self._open_fpaths.append(fpath)
        
    def close_file(self, openFileNo : int):
        """Closes file spcified relative to the project dirpath"""
        fpath = self._open_fpaths[openFileNo]
        self._open_fpaths.remove(fpath)

    def run_file(self, openFileNo : int):
        fpath = self._open_fpaths[openFileNo]
        env, cwd = {'PYTHONPATH': self.proj_dirpath}, self.proj_dirpath
        arg_list = [self.interpreter_fpath, fpath]
        result = subprocess.run(arg_list, capture_output=True, text=True, env=env, cwd=cwd)

        script_stdout = f'{result.stdout}'
        script_stderr = f'\033[31m{result.stderr}\033[0m'
        exit_code_msg = f'Process finished with exit code {result.returncode}'

        self.output_map[fpath] = f'{fpath}\n{script_stdout}{script_stderr}\n{exit_code_msg}'

    def replace(self, fileNo : int, start_line : int, end_line : int, content : str):
        """Replaces lines starting from [line_start] to [line_end] including start and end in fileNo [fileNo] with new [content]"""
        fpath = self._open_fpaths[fileNo]
        with open(fpath, 'r') as f:
            file_lines = f.read().split('\n')
            content_lines = content.split('\n') if content else []
            newlines = file_lines[:start_line-1] + content_lines + file_lines[end_line:]
        new_content = '\n'.join(newlines)
        with open(fpath, 'w') as f:
            f.write(new_content)

    def insert(self, fileNo : int, after_line : int, content : str):
        """Inserts [content] at line [line] in fileNo [fileNo]"""
        fpath = self._open_fpaths[fileNo]
        with open(fpath, 'r') as f:
            file_lines = f.read().split('\n')
            content_lines = content.split('\n')
            newlines = file_lines[:after_line] + content_lines + file_lines[after_line:]
        new_content = '\n'.join(newlines)
        with open(fpath, 'w') as f:
            f.write(new_content)

    def _get_abspath(self, fpath : str):
        fpath= os.path.expanduser(fpath)
        if os.path.isabs(fpath):
            return fpath
        else:
            return os.path.join(self.proj_dirpath, fpath)

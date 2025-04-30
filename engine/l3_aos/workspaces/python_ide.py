import os
from typing import Optional

from PIL.Image import Image as PILImage
import subprocess
import re

from engine.l3_aos.workspaces.workspace import Workspace
from holytools.fsys import Directory
from holytools.userIO import MessageFormatter
from pylint import lint
from pylint.reporters import CollectingReporter

# --------------------------------------------

class PythonIDE(Workspace):
    """LotusPythonIDE: Minimal text operable python IDE"""
    def __init__(self):
        super().__init__()
        self.proj_dirpath : Optional[str] = None
        self.interpreter_fpath : Optional[str] = None
        self.viewprovider : Optional[ViewProvider] = None

        self.output_map : dict[str, str] = {}
        self._open_fpaths : list[str] = []

    # -------------------------------------------------------
    # Workspace generics

    def open(self, project_dirpath : str):
        """Starts a minimal text operable python IDE only available to you. Use for python development tasks."""
        project_dirpath = os.path.expanduser(project_dirpath)
        if not os.path.isdir(project_dirpath):
            raise ValueError(f'Project dirpath does not exist: {project_dirpath}')
        self._reset()

        self.proj_dirpath = project_dirpath
        py_fpath = os.path.join(self.proj_dirpath, '.venv/bin/python')
        if not os.path.isfile(py_fpath):
            self._mkvenv(proj_dirpath=self.proj_dirpath)

        self.interpreter_fpath: Optional[str] = py_fpath
        self.viewprovider = ViewProvider(proj_dirpath=self.proj_dirpath)

    def close(self, *args, **kwargs):
        self._reset()

    def _reset(self):
        self.proj_dirpath = None
        self.output_map = {}
        self._open_fpaths = []
        self.interpreter_fpath = None
        self.viewprovider = None

    def get_text(self) -> str:
        metadata = self.viewprovider.get_metadata(interpreter_fpath=self.interpreter_fpath)
        filetree = self.viewprovider.get_project_filetree()
        editor = self.viewprovider.get_editor(open_fpaths=self._open_fpaths, run_output=self.output_map)

        text = MessageFormatter.get_boxed(text=metadata, headline=f'Project metadata')
        text += MessageFormatter.get_boxed(text=filetree, headline=f'Project file structure ({self.proj_dirpath})')
        if self._open_fpaths:
            text += editor

        return text

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
        
    def write(self, fileNo : int, after_line : int, content : str):
        """Writes content to a file opened in the IDE"""
        fpath = self._open_fpaths[fileNo]
        if os.path.isfile(path=fpath):
            with open(fpath, 'r') as f:
                lines = f.readlines()

            before_content = ''.join(lines[:after_line])
            after_content = ''.join(lines[after_line:])
            content = f'{before_content}{content}\n{after_content}'

        with open(fpath, 'w') as f:
            f.write(content)

    def delete(self, fileNo :int, start_line : int,end_line : int ):
        """Deletes lines in a file opened in the IDE"""
        fpath = self._open_fpaths[fileNo]
        with open(fpath, 'r') as f:
            lines = f.readlines()

        before_lines = lines[:start_line-1]
        after_lines = lines[end_line:]
        total_lines = before_lines + after_lines

        new_content = ''.join(total_lines)
        with open(fpath, 'w') as f:
            f.write(new_content)

    def _get_abspath(self, fpath : str):
        fpath= os.path.expanduser(fpath)
        if os.path.isabs(fpath):
            return fpath
        else:
            return os.path.join(self.proj_dirpath, fpath)

    @staticmethod
    def _mkvenv(proj_dirpath : str):
        subprocess.run(['python3', '-m', 'venv', f'{proj_dirpath}/.venv'])



class ViewProvider:
    def __init__(self, proj_dirpath : str):
        self.proj_dirpath : str = proj_dirpath
        self.excluded_patterns : list[str] = ['.*\\.pyc']
        self.excluded_dirs : list[str] = ['.venv', '.git', '.idea']

    def get_metadata(self, interpreter_fpath : str) -> str:
        venv = os.path.relpath(interpreter_fpath, self.proj_dirpath) if interpreter_fpath else None
        metadata = (f'{"Project name":<20}: {os.path.basename(self.proj_dirpath)}\n'
                    f'{"Project dirpath":<20}: {self.proj_dirpath} \n'
                    f'{"Virtual environment":<20}: {venv}')
        return metadata

    def get_project_filetree(self) -> str:
        root_node = Directory(path=self.proj_dirpath)
        fpaths = root_node.get_subfile_fpaths()
        fpaths = [p for p in fpaths if not self._is_excluded(fpath=p)]
        fs_dict = root_node.to_dict(fpaths=fpaths)

        parts = self.proj_dirpath.split('/')
        for p in parts:
            fs_dict = fs_dict[p]

        filetree = root_node.dict_to_tree(fs_dict=fs_dict, parent_dirpath=self.proj_dirpath, max_children=10)

        return filetree

    def _is_excluded(self, fpath : str) -> bool:
        excluded_dirpaths = [os.path.join(self.proj_dirpath, excl_dir) for excl_dir in self.excluded_dirs]
        in_excluded = any([fpath.startswith(excl_path) for excl_path in excluded_dirpaths])
        
        excluded_reg_patterns = [re.compile(pattern) for pattern in self.excluded_patterns]
        matches_exclusion_pattern = any([pattern.match(fpath) for pattern in excluded_reg_patterns])

        return in_excluded or matches_exclusion_pattern

    @staticmethod
    def get_editor(open_fpaths : list[str], run_output : dict[str, str]) -> str:
        all_contents = ''
        for j, path in enumerate(open_fpaths):
            fname = os.path.basename(path)
            texts = [ViewProvider._get_with_lineno(fpath=path), ViewProvider._get_inspections(fpath=path)]
            headlines = [f'[{fname} (fileNo: {j})]', 'Problems']

            if path in run_output:
                texts.append(run_output[path])
                headlines.append('Execution output')

            all_contents += MessageFormatter.multi_section_box(texts=texts, headlines=headlines)

        return all_contents

    @staticmethod
    def _get_inspections(fpath : str) -> str:
        reporter = CollectingReporter()
        lint.Run([fpath] + ['--disable=C,R'], reporter=reporter, exit=False)
        criticalility_dict = {'W' : '⚠️', 'E' : '🛑'}

        formatted_inspections = ''
        for m in reporter.messages:
            symbol = criticalility_dict[m.C]
            formatted_inspections += f' {symbol} l.{m.line:<4}| {m.msg}\n'

        return formatted_inspections

    @staticmethod
    def _get_with_lineno(fpath : str) -> str:
        with open(fpath, 'r') as f:
            c = f.read()
        lines = c.split('\n')

        enumerated_content = ''
        for n, l in enumerate(lines):
            enumerated_content += f'{n+1:< 5}| {l}\n'
        enumerated_content = enumerated_content.rstrip('\n')
        return enumerated_content

    #
    #
    # def install_libraries(self, names : list[str]):
    #     subprocess.run([self.interpreter_fpath, '-m' 'pip', 'install'] + names)

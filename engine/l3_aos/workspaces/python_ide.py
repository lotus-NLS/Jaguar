import os
from typing import Optional

from PIL.Image import Image as PILImage
import subprocess
from engine.l3_aos import Workspace
import re

from holytools.fsys import Directory
from holytools.userIO import MessageFormatter
from pylint import lint
from pylint.reporters import CollectingReporter

# --------------------------------------------

class PythonIDE(Workspace):
    """LotusPythonIDE: Minimal text operable python IDE"""
    def __init__(self):
        super().__init__()
        self.project : Optional[PythonProject] = None

    def switch_project(self, workspace_dirpath : str):
        self.project = PythonProject(project_dirpath=workspace_dirpath)

    def run_file(self, script_fpath : str):
        self.project.run_file(script_fpath=script_fpath)

    def open_file(self, fpath : str):
        """Opens a file specified relative to the project dirpath. If the file does not exist it is created instead"""
        self.project.open_file(fpath=fpath)

    def close_file(self, fpath : str):
        """Closes file spcified relative to the project dirpath"""
        self.project.close_file(fpath=fpath)

    # -------------------------------------------------------
    # Workspace generics

    def open(self, project_dirpath : str):
        """Starts a minimal text operable python IDE only available to you. Use for python development tasks."""
        self.project = PythonProject(project_dirpath=project_dirpath)

    def close(self, *args, **kwargs):
        self.project = None

    def get_text(self) -> str:
        return self.project.get_view()

    def get_image(self) -> Optional[PILImage]:
        return None


class PythonProject:
    def __init__(self, project_dirpath : str):
        project_dirpath = os.path.expanduser(project_dirpath)
        if not os.path.isdir(project_dirpath):
            raise ValueError(f'Project dirpath does not exist: {project_dirpath}')

        self.dirpath : str = project_dirpath
        if not self.dirpath:
            raise ValueError(f'Project dirpath does not exist: {self.dirpath}')
        venv_python_fpath = os.path.join(self.dirpath, '.venv/bin/python')
        self.interpreter_fpath : Optional[str] = venv_python_fpath if os.path.isfile(venv_python_fpath) else None

        self.excluded_dirs : list[str] = ['.venv', '.git', '.idea']
        self.excluded_patterns : list[str] = ['.*\\.pyc']

        self.run_output : Optional[str] = None
        self._open_fpaths : list[str] = []


    def open_file(self, fpath : str):
        fpath = self._get_abspath(fpath=fpath)
        parent_dir = os.path.dirname(fpath)
        if not os.path.isdir(parent_dir):
            raise ValueError(f'Parent directory of file does not exist: {parent_dir}')
        if not os.path.isfile(fpath):
            with open(fpath, 'w') as f:
                f.write('')

        fpath = self._get_abspath(fpath=fpath)
        self._open_fpaths.append(fpath)

    def close_file(self, fpath : str):
        fpath = self._get_abspath(fpath=fpath)
        self._open_fpaths.remove(fpath)

    def write(self, fileNo : int, after_line : int, content : str):
        fpath = self._open_fpaths[fileNo]
        if os.path.isfile(path=fpath):
            with open(fpath, 'r') as f:
                lines = f.readlines()

            before_lines = lines[:after_line]
            content_lines = content.split('\n')
            after_lines =  lines[after_line:]
            total_lines = before_lines + content_lines + ['\n'] + after_lines

            content = ''.join(total_lines)

        with open(fpath, 'w') as f:
            f.write(content)

    def delete(self, fileNo :int, start_line : int,end_line : int ):
        fpath = self._open_fpaths[fileNo]
        with open(fpath, 'r') as f:
            lines = f.readlines()

        before_lines = lines[:start_line-1]
        after_lines = lines[end_line:]
        total_lines = before_lines + after_lines

        new_content = ''.join(total_lines)
        with open(fpath, 'w') as f:
            f.write(new_content)


    def mkvenv(self):
        subprocess.run(['python3', '-m', 'venv', f'{self.dirpath}/.venv'])
        self.interpreter_fpath = os.path.join(self.dirpath, '.venv/bin/python')

    def install_libraries(self, names : list[str]):
        subprocess.run([self.interpreter_fpath, '-m' 'pip', 'install'] + names)

    def run_file(self, script_fpath : str):
        env = {'PYTHONPATH' : self.dirpath}
        result = subprocess.run([self.interpreter_fpath, script_fpath], capture_output=True, text=True, env=env)
        script_stdout = f'{result.stdout}'
        script_stderr = f'\033[31m{result.stderr}\033[0m'
        exit_code_msg = f'Process finished with exit code {result.returncode}'

        self.run_output = f'{script_fpath}\n{script_stdout}{script_stderr}\n{exit_code_msg}'

    def get_view(self) -> str:
        text = MessageFormatter.get_boxed(text=self._get_metadata(), headline=f'Project metadata')
        text += MessageFormatter.get_boxed(text=self._get_project_filetree(), headline=f'Project file structure')
        if self._open_fpaths:
            text += self._get_editor()
        if self.run_output:
            text += MessageFormatter.get_boxed(headline='Execution output', text=self.run_output)

        return text

    # -----------------------------------------------

    def _get_abspath(self, fpath : str):
        fpath= os.path.expanduser(fpath)
        if os.path.isabs(fpath):
            return fpath
        else:
            return os.path.join(self.dirpath, fpath)

    def _get_metadata(self) -> str:
        venv = os.path.relpath(self.interpreter_fpath, self.dirpath) if self.interpreter_fpath else None
        metadata = (f'{"Project name":<20}: {os.path.basename(self.dirpath)}\n'
                    f'{"Project dirpath":<20}: {self.dirpath} \n'
                    f'{"Virtual environment":<20}: {venv}')
        return metadata

    def _get_project_filetree(self):
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

    def _get_editor(self) -> str:
        all_contents = ''
        for j, path in enumerate(self._open_fpaths):
            fname = os.path.basename(path)
            texts = [self._view_with_lineno(fpath=path), self._get_inspections(fpath=path)]
            headlines = [f'[{fname} (fileNo: {j})]', 'Problems']
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
    def _view_with_lineno(fpath : str):
        with open(fpath, 'r') as f:
            c = f.read()
        lines = c.split('\n')

        enumerated_content = ''
        for n, l in enumerate(lines):
            enumerated_content += f'{n+1:< 5}| {l}\n'
        enumerated_content = enumerated_content.rstrip('\n')
        return enumerated_content


if __name__ == "__main__":
    test_dirpath = '/home/daniel/testdir'
    testscript_fpath = os.path.join(test_dirpath, 'srcdir/newfile.py')

    project = PythonProject(project_dirpath=test_dirpath)
    project.open_file(fpath=testscript_fpath)
    project.install_libraries(names=['pipdeptree', 'deptry'])

    print(project.get_view())

import os
import re

from pylint import lint
from pylint.reporters import CollectingReporter

from holytools.fsys import Directory
from holytools.userIO import MessageFormatter


class PythonEditor:
    def __init__(self, proj_dirpath : str, interpreter_fpath : str):
        self.proj_dirpath : str = proj_dirpath
        self.interpreter_fpath : str = interpreter_fpath

        self.excluded_patterns : list[str] = ['.*\\.pyc', '.*/__pycache__/.*']
        self.excluded_dirs : list[str] = ['.venv', '.git', '.idea', 'build']
    
    def get_view(self, open_fpaths : list[str], run_output : dict[str, str]):
        metadata = self.get_metadata()
        filetree = self.get_project_filetree()
        editor = self.get_editor(open_fpaths=open_fpaths, run_output=run_output)

        view = MessageFormatter.get_boxed(text=metadata, headline=f'Project metadata')
        view += MessageFormatter.get_boxed(text=filetree, headline=f'Project file structure ({self.proj_dirpath})')
        if open_fpaths:
            view += editor

        return view

    @staticmethod
    def replace(fpath : str, line_start : int, line_end : int, content : str):
        with open(fpath, 'r') as f:
            file_lines = f.read().split('\n')
            content_lines = content.split('\n') if content else []
            newlines = file_lines[:line_start-1] + content_lines + file_lines[line_end:]
        new_content = '\n'.join(newlines)
        with open(fpath, 'w') as f:
            f.write(new_content)

    @staticmethod
    def insert(fpath : str, after_line : int, content : str):
        with open(fpath, 'r') as f:
            file_lines = f.read().split('\n')
            content_lines = content.split('\n')
            newlines = file_lines[:after_line] + content_lines + file_lines[after_line:]
        new_content = '\n'.join(newlines)
        with open(fpath, 'w') as f:
            f.write(new_content)

    def get_metadata(self) -> str:
        venv = os.path.relpath(self.interpreter_fpath, self.proj_dirpath) if self.interpreter_fpath else None
        metadata = (f'{"Project name":<20}: {os.path.basename(self.proj_dirpath)}\n'
                    f'{"Project dirpath":<20}: {self.proj_dirpath} \n'
                    f'{"Virtual environment":<20}: {venv}')
        return metadata

    def get_project_filetree(self) -> str:
        root_node = Directory(path=self.proj_dirpath)
        fpaths = root_node.get_subfile_fpaths()
        fpaths = [p for p in fpaths if not self.is_excluded(fpath=p)]
        fs_dict = root_node.to_dict(fpaths=fpaths)

        parts = self.proj_dirpath.split('/')
        for p in parts:
            fs_dict = fs_dict[p]

        filetree = root_node.dict_to_tree(fs_dict=fs_dict, parent_dirpath=self.proj_dirpath, max_children=10)

        return filetree

    def is_excluded(self, fpath : str) -> bool:
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
            texts = [PythonEditor._get_with_lineno(fpath=path), PythonEditor._get_inspections(fpath=path)]
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

import os
import re
from typing import Optional

from pylint import lint
from pylint.reporters import CollectingReporter

from holytools.fsys import Directory
from holytools.fsys.tree import TreeGenerator
from holytools.userIO import MessageFormatter


class ProjectView:
    def __init__(self, proj_dirpath : str):
        self.proj_dirpath : str = proj_dirpath
        self.excluded_patterns : list[str] = ['.*\\.pyc', '.*/__pycache__/.*', '.*\.egg-info']
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

    def get_metadata(self, venv_dirpath : Optional[str] = None) -> str:
        metadata = (f'{"Project name":<20}: {os.path.basename(self.proj_dirpath)}'
                    f'\n{"Project dirpath":<20}: {self.proj_dirpath}')
        if not venv_dirpath is None:
            metadata += f'\n{"Virtual environment":<20}: {venv_dirpath}'

        return metadata

    def get_project_filetree(self, desc_map : Optional[dict[str,str]] = None) -> str:
        root_node = Directory(path=self.proj_dirpath)
        fpaths = root_node.get_subfile_fpaths()
        fpaths = [p for p in fpaths if not self.is_excluded(fpath=p)]

        fsys_dict = TreeGenerator.to_dict(fpaths=fpaths)
        for p in self.proj_dirpath.split('/'):
            fsys_dict = fsys_dict[p]

        filetree = TreeGenerator.dict_to_tree(fsys_dict=fsys_dict, desc_map=desc_map, parent_dirpath=self.proj_dirpath, max_children=10)
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
            texts = [ProjectView._get_with_lineno(fpath=path), ProjectView._get_inspections(fpath=path)]
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


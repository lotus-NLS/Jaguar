from __future__ import annotations
import os
import re
from typing import Optional

from pylint import lint
from pylint.reporters import CollectingReporter

from holytools.userIO import MessageFormatter


# -----------------------------------------------------
class PythonEditor:
    @staticmethod
    def get_info(proj_dirpath : str, venv_dirpath: Optional[str] = None) -> str:
        metadata = (f'{"Project name":<20}: {os.path.basename(proj_dirpath)}'
                    f'\n{"Project dirpath":<20}: {proj_dirpath}')
        if not venv_dirpath is None:
            metadata += f'\n{"Virtual environment":<20}: {venv_dirpath}'

        return metadata

    @classmethod
    def get_editor(cls, open_fpaths: list[str], run_output: dict[str, str]) -> str:
        all_contents = ''
        for j, path in enumerate(open_fpaths):
            fname = os.path.basename(path)
            texts = [cls._get_file_with_lineno(fpath=path), cls._get_inspections(fpath=path)]
            headlines = [f'[{fname} (fileNo: {j})]', 'Problems']

            if path in run_output:
                texts.append(run_output[path])
                headlines.append('Execution output')

            all_contents += MessageFormatter.multi_section_box(texts=texts, headlines=headlines)

        return all_contents

    @staticmethod
    def _get_inspections(fpath: str) -> str:
        reporter = CollectingReporter()
        lint.Run([fpath] + ['--disable=C,R'], reporter=reporter, exit=False)
        criticalility_dict = {'W': '⚠️', 'E': '🛑'}

        formatted_inspections = ''
        for m in reporter.messages:
            symbol = criticalility_dict[m.C]
            formatted_inspections += f' {symbol} l.{m.line:<4}| {m.msg}\n'

        return formatted_inspections


    @staticmethod
    def _get_file_with_lineno(fpath: str) -> str:
        with open(fpath, 'r') as f:
            c = f.read()
        lines = c.split('\n')

        enumerated_content = ''
        for n, l in enumerate(lines):
            enumerated_content += f'{n + 1:< 5}| {l}\n'
        enumerated_content = enumerated_content.rstrip('\n')
        return enumerated_content


class ProjectNode:
    def __init__(self, path : str, idx : Optional[int] = None, desc : Optional[str] = None):
        self.path = path
        self.idx : int = idx
        self.description : str = desc
        self.children : list[ProjectNode] = []
        self.excluded_patterns : list[str] = ['.*\\.pyc', '.*/__pycache__', '.*\\.egg-info',
                                              '.*/.venv', '.*.git.*', '.*\\.idea.*', '.*build.*']

    def fill_ancestors(self, desc_map : dict[str, str], path_to_ID : dict[str, int]):
        if os.path.isfile(self.path):
            return

        subnode_names = os.listdir(self.path)
        subnode_paths = [os.path.join(self.path, name) for name in subnode_names]
        subnode_paths = [os.path.abspath(p) for p in subnode_paths if not self.is_excluded(fpath=p)]
        subnodes = [ProjectNode(path=p, desc=desc_map.get(p), idx=path_to_ID.get(p)) for p in subnode_paths]

        dir_nodes = [subnode for subnode in subnodes if os.path.isdir(subnode.path)]
        file_nodes = [subnode for subnode in subnodes if os.path.isfile(subnode.path)]
        for f in file_nodes:
            self.children.append(f)
        for d in dir_nodes:
            self.children.append(d)
            d.fill_ancestors(desc_map=desc_map, path_to_ID=path_to_ID)

    def is_excluded(self, fpath : str) -> bool:
        regex_patterns = [re.compile(pattern) for pattern in self.excluded_patterns]
        matches_exclusion = any([pattern.match(fpath) for pattern in regex_patterns])
        return matches_exclusion

    def get_tree(self, indent : int = 0) -> str:
        symbol = '🗎' if os.path.isfile(self.path) else '🗀'
        indentation = '\t' * indent
        cond_desc = f'\n{indentation}{self.description}' if self.description else ""
        cond_idx = f' | FileID = {self.idx}' if self.idx is not None else ''
        cond_backslash = '/' if os.path.isdir(self.path) else ''

        total_str = (f'{indentation}{symbol} {self.get_name()}{cond_backslash}{cond_idx}'
                     f'{cond_desc}')
        for subnode in self.children:
            total_str += f'\n{subnode.get_tree(indent=indent+1)}'

        return total_str

    def get_name(self) -> str:
        return os.path.basename(self.path)

    def get_fpath_fileID_map(self) -> dict[str, int]:

        pass

    def get_ancestors(self) -> list[ProjectNode]:
        if os.path.isfile(self.path):
            return []
        ancestors = self.children
        for n in [c for c in self.children if c.is_dir()]:
            ancestors += n.get_ancestors()
        return ancestors

    def is_dir(self) -> bool:
        return os.path.isdir(self.path)

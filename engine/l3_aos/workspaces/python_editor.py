import os
import re
from typing import Optional

from pylint import lint
from pylint.reporters import CollectingReporter

from holytools.userIO import MessageFormatter


# -----------------------------------------------------



class ProjectView:
    def __init__(self, proj_dirpath : str):
        self.proj_dirpath : str = proj_dirpath
        self.excluded_patterns : list[str] = ['.venv', '.git', '.idea', 'build', '.*\\.pyc', '.*/__pycache__/.*', '.*\\.egg-info']

    def get_view(self, open_fpaths : list[str], run_output : dict[str, str],
                 path_to_id : Optional[dict[str, int]] = None):
        metadata = self.get_metadata()
        filetree = self.get_project_filetree(path_to_fileID=path_to_id, desc_map={})
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

    def get_project_filetree(self, desc_map : dict[str,str], path_to_fileID : dict[str, int]) -> str:
        root_node = Node(path=self.proj_dirpath,desc=desc_map.get(self.proj_dirpath, None))
        root_node.fill_ancestors(exclude_patterns=self.excluded_patterns,desc_map=desc_map,path_to_idx=path_to_fileID)
        return root_node.get_tree()

    @staticmethod
    def get_editor(open_fpaths : list[str], run_output : dict[str, str]) -> str:
        all_contents = ''
        for j, path in enumerate(open_fpaths):
            fname = os.path.basename(path)
            texts = [ProjectView._get_file_with_lineno(fpath=path), ProjectView._get_inspections(fpath=path)]
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
    def _get_file_with_lineno(fpath : str) -> str:
        with open(fpath, 'r') as f:
            c = f.read()
        lines = c.split('\n')

        enumerated_content = ''
        for n, l in enumerate(lines):
            enumerated_content += f'{n+1:< 5}| {l}\n'
        enumerated_content = enumerated_content.rstrip('\n')
        return enumerated_content



class Node:
    def __init__(self, path : str, idx : Optional[int] = None, desc : Optional[str] = None):
        self.path = path
        self.idx : int = idx
        self.description : str = desc
        self.children : list[Node] = []

    def fill_ancestors(self, exclude_patterns : list[str], desc_map : dict[str, str], path_to_idx : dict[str, int]):
        if os.path.isfile(self.path):
            return

        subnode_names = os.listdir(self.path)
        subnode_paths = [os.path.join(self.path, name) for name in subnode_names]
        subnode_paths = [os.path.abspath(p) for p in subnode_paths if not self.is_excluded(fpath=p, exclude_patterns=exclude_patterns)]
        subnodes = [Node(path=p, desc=desc_map.get(p), idx=path_to_idx.get(p)) for p in subnode_paths]

        dir_nodes = [subnode for subnode in subnodes if os.path.isdir(subnode.path)]
        file_nodes = [subnode for subnode in subnodes if os.path.isfile(subnode.path)]
        for f in file_nodes:
            self.children.append(f)
        for d in dir_nodes:
            self.children.append(d)
            d.fill_ancestors(exclude_patterns=exclude_patterns, desc_map=desc_map, path_to_idx=path_to_idx)

    def get_tree(self, indent : int = 0) -> str:
        symbol = '🗎' if os.path.isfile(self.path) else '🗀'
        indentation = '\t' * indent
        cond_desc = f'n{self.description}' if self.description else ""
        cond_idx = f' | ID = {self.idx}' if self.idx is not None else ''
        cond_backslash = '/' if os.path.isdir(self.path) else ''

        total_str = (f'{indentation}{symbol} {self.get_name()}{cond_backslash}{cond_idx}'
                     f'{cond_desc}')
        for subnode in self.children:
            total_str += subnode.get_tree(indent=indent+1)

        return total_str

    def get_name(self) -> str:
        return os.path.basename(self.path)

    @staticmethod
    def is_excluded(fpath : str, exclude_patterns : list[str]) -> bool:
        regex_patterns = [re.compile(pattern) for pattern in exclude_patterns]
        matches_exclusion = any([pattern.match(fpath) for pattern in regex_patterns])

        return matches_exclusion
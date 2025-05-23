from __future__ import annotations
import os
import re
from typing import Optional

# -------------------------------------------------


class ProjectNode:
    def __init__(self, path : str, idx : Optional[int] = None, desc : Optional[str] = None):
        self.path = path
        self.idx : int = idx
        self.description : str = desc
        self.children : list[ProjectNode] = []
        self.excluded_patterns : list[str] = ['.*\\.pyc', '.*/__pycache__', '.*\\.egg-info',
                                              '.*/.venv', '.*.git.*', '.*\\.idea.*', '.*build.*']

    def fill_ancestors(self, desc_map : dict[str, str]):
        if os.path.isfile(self.path):
            return

        subnode_names = os.listdir(self.path)
        subnode_paths = [os.path.join(self.path, name) for name in subnode_names]
        subnode_paths = [os.path.abspath(p) for p in subnode_paths if not self.is_excluded(fpath=p)]
        subnodes = [ProjectNode(path=p, desc=desc_map.get(p)) for p in subnode_paths]

        dir_nodes = [subnode for subnode in subnodes if os.path.isdir(subnode.path)]
        file_nodes = [subnode for subnode in subnodes if os.path.isfile(subnode.path)]
        for f in file_nodes:
            self.children.append(f)
        for d in dir_nodes:
            self.children.append(d)
            d.fill_ancestors(desc_map=desc_map)

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
        ancestors = self.get_ancestors()
        file_ancestors = [node for node in ancestors if os.path.isfile(node.path)]
        return {node.path : j for j,node in enumerate(file_ancestors)}

    def get_ancestors(self) -> list[ProjectNode]:
        if os.path.isfile(self.path):
            return []
        ancestors = self.children
        for n in [c for c in self.children if c.is_dir()]:
            ancestors += n.get_ancestors()
        return ancestors

    def is_dir(self) -> bool:
        return os.path.isdir(self.path)
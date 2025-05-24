from __future__ import annotations
import os
import re
from typing import Optional

# -------------------------------------------------


class ProjectNode:
    def __init__(self, path : str, idx : Optional[int] = None, desc : Optional[str] = None):
        self.path = path
        self.description : str = desc
        self.children : list[ProjectNode] = []
        self.idx : Optional[int] = idx
        self.excluded_patterns : list[str] = ['.*\\.pyc', '.*/__pycache__', '.*\\.egg-info',
                                              '.*/.venv', '.*.git.*', '.*\\.idea.*', '.*build.*']

    def fill_ancestors(self, desc_map : dict[str, str]):
        if self.path in desc_map:
            self.description = desc_map[self.path]

        if os.path.isfile(self.path):
            return

        self.children = []
        subnode_names = os.listdir(self.path)
        subnode_paths = [os.path.join(self.path, name) for name in subnode_names]
        subnode_paths = [os.path.abspath(p) for p in subnode_paths if not self.is_excluded(fpath=p)]
        subnodes = [ProjectNode(path=p, desc=desc_map.get(p)) for p in subnode_paths]

        dir_nodes = [sn for sn in subnodes if os.path.isdir(sn.path)]
        file_nodes = [sn for sn in subnodes if os.path.isfile(sn.path)]
        for f in file_nodes:
            self.children.append(f)
        for d in dir_nodes:
            self.children.append(d)
            d.fill_ancestors(desc_map=desc_map)

        fileID = 0
        ancestors = self.get_ancestors()
        for node in ancestors:
            if not node.is_dir():
                node.idx = fileID
                fileID += 1

    def is_excluded(self, fpath : str) -> bool:
        regex_patterns = [re.compile(pattern) for pattern in self.excluded_patterns]
        matches_exclusion = any([pattern.match(fpath) for pattern in regex_patterns])
        return matches_exclusion

    def get_tree(self, show_idx : bool = False, show_desc : bool = False, indent : int = 0) -> str:
        symbol = '🗎' if os.path.isfile(self.path) else '🗀'
        indentation = '\t' * indent
        cond_desc = f'\n{indentation}{self.description}' if self.description and show_desc else ""
        cond_idx = f' | FileID = {self.idx}' if self.idx is not None and show_idx else ''
        cond_backslash = '/' if os.path.isdir(self.path) else ''

        total_str = (f'{indentation}{symbol} {self.get_name()}{cond_backslash}{cond_idx}'
                     f'{cond_desc}')
        for subnode in self.children:
            total_str += f'\n{subnode.get_tree(indent=indent+1, show_idx=show_idx, show_desc=show_desc)}'

        return total_str

    def get_name(self) -> str:
        return os.path.basename(self.path)

    def get_path_to_idx(self) -> dict[str, int]:
        ancestor_nodes = self.get_ancestors()
        return {node.path : node.idx for node in ancestor_nodes}

    def get_ancestors(self) -> list[ProjectNode]:
        if os.path.isfile(self.path):
            return []
        ancestors = [x for x in self.children]
        for n in [c for c in self.children if c.is_dir()]:
            ancestors += n.get_ancestors()
        return ancestors

    def is_dir(self) -> bool:
        return os.path.isdir(self.path)
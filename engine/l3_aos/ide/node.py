from __future__ import annotations
import os
import re
from typing import Optional

# -------------------------------------------------


class SourceNode:
    def __init__(self, source_path : str, idx : Optional[int] = None, comment : Optional[str] = None):
        self.source_path = source_path
        self.comment : str = comment
        self.children : list[SourceNode] = []
        self.idx : Optional[int] = idx

    @classmethod
    def ancestor(cls, source_path : str, is_root : bool = True) -> SourceNode:
        parent = cls(source_path=source_path)
        if os.path.isfile(source_path):
            return parent

        child_paths = [os.path.join(source_path, name) for name in sorted(os.listdir(source_path))]
        child_paths = [p for p in child_paths if not cls.is_excluded(fpath=p)]
        parent.children += [cls.ancestor(source_path=p, is_root=False) for p in child_paths if os.path.isdir(p)]
        parent.children += [cls.ancestor(source_path=p, is_root=False) for p in child_paths if os.path.isfile(p)]

        if is_root:
            fileID = 0
            for node in parent.get_descendants():
                if not os.path.isdir(node.source_path):
                    node.idx = fileID
                    fileID += 1

        return parent

    def get_descendants(self) -> list[SourceNode]:
        ancestors = [x for x in self.children]
        for n in [c for c in self.children if os.path.isdir(self.source_path)]:
            ancestors += n.get_descendants()
        return ancestors

    @staticmethod
    def is_excluded(fpath : str) -> bool:
        excluded_patterns: list[str] = ['.*\\.pyc', '.*/__pycache__', '.*\\.egg-info',
                                        '.*/.venv', '.*.git.*', '.*\\.idea.*', '.*build.*']

        regex_patterns = [re.compile(pattern) for pattern in excluded_patterns]
        matches_exclusion = any([pattern.match(fpath) for pattern in regex_patterns])
        return matches_exclusion

    # --------------------------------------------------
    # Index resolution

    def get_path(self, idx : int):
        idx_to_path = {node.idx : node.source_path for node in self.get_descendants()}
        return idx_to_path[idx]

    def get_idx(self, path : str):
        path_to_idx = {node.source_path : node.idx for node in self.get_descendants()}
        return path_to_idx[path]

    # ---------------------------------------------
    # Properties

    def get_tree(self, show_idx : bool = False, show_desc : bool = False, indent : int = 0) -> str:
        symbol = '🗎' if os.path.isfile(self.source_path) else '🗀'
        indentation = '\t' * indent
        cond_desc = f'\n{indentation}{self.comment}' if self.comment and show_desc else ""
        cond_idx = f' | FileID = {self.idx}' if self.idx is not None and show_idx else ''
        cond_backslash = '/' if os.path.isdir(self.source_path) else ''

        total_str = (f'{indentation}{symbol} {self.get_name()}{cond_backslash}{cond_idx}'
                     f'{cond_desc}')
        for subnode in self.children:
            total_str += f'\n{subnode.get_tree(indent=indent+1, show_idx=show_idx, show_desc=show_desc)}'

        return total_str

    def get_name(self) -> str:
        return os.path.basename(self.source_path)

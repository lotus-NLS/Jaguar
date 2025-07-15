from __future__ import annotations
import os
import re
from typing import Optional, Any


# -------------------------------------------------


class SourceNode:
    def __init__(self, source_path : str, ancestors : list[SourceNode]):
        self.source_path = source_path
        self.ancestors : list = ancestors
        self.idx : Optional[int] = None
        self.children : list[SourceNode] = []

    @classmethod
    def create_tree(cls, source_path : str, ancestors : Optional[list[SourceNode]] = None) -> SourceNode:
        parent = cls(source_path=source_path, ancestors=ancestors)
        if os.path.isfile(path=source_path):
            return parent

        child_paths = [os.path.join(source_path, name) for name in sorted(os.listdir(source_path))]
        child_paths = [p for p in child_paths if not cls.is_excluded(fpath=p)]

        child_ancestors = [parent] if ancestors is None else ancestors + [parent]
        parent.children += [cls.create_tree(source_path=p, ancestors=child_ancestors) for p in child_paths if os.path.isfile(p)]
        parent.children += [cls.create_tree(source_path=p, ancestors=child_ancestors) for p in child_paths if os.path.isdir(p)]

        if ancestors is None:
            fileID = 0
            for node in parent.get_descendants():
                if not os.path.isdir(node.source_path):
                    node.idx = fileID
                    fileID += 1

        return parent

    def get_descendants(self) -> list[SourceNode] | list[Any]:
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

    def get_tree(self, show_idx : bool = False, show_comments : bool = False, indent : int = 0) -> str:
        comment = self.get_desc()

        symbol = '🗎' if os.path.isfile(self.source_path) else '🗀'
        indentation = '\t' * indent
        cond_comment = f'\n{indentation}{comment}' if comment and show_comments else ""
        cond_idx = f' | FileID = {self.idx}' if not self.idx is None and show_idx else ''
        cond_backslash = '/' if os.path.isdir(self.source_path) else ''

        total_str = (f'{indentation}{symbol} {self.get_name()}{cond_backslash}{cond_idx}'
                     f'{cond_comment}')
        for subnode in self.children:
            total_str += f'\n{subnode.get_tree(show_idx, show_comments, indent + 1)}'

        return total_str

    def get_name(self) -> str:
        return os.path.basename(self.source_path)

    def get_desc(self) -> Optional[str]:
        pass
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Optional

from holytools.abstract import TreeNode

# -------------------------------------------------



@dataclass
class SourceNode(TreeNode):
    source_path : str
    parent: SourceNode
    children: list[SourceNode] = field(default_factory=list)

    @classmethod
    def create_tree(cls, source_path : str, parent : Optional[SourceNode] = None) -> SourceNode:
        root = cls(source_path=source_path, parent=parent, name=os.path.basename(source_path))
        if os.path.isfile(path=source_path):
            return root

        child_paths = [os.path.join(source_path, name) for name in sorted(os.listdir(source_path))]
        child_paths = [p for p in child_paths if not cls.is_excluded(fpath=p)]

        root.children += [cls.create_tree(source_path=p, parent=root) for p in child_paths if os.path.isfile(p)]
        root.children += [cls.create_tree(source_path=p, parent=root) for p in child_paths if os.path.isdir(p)]

        return root

    def is_indexable(self) -> bool:
        return os.path.isfile(self.source_path)

    @staticmethod
    def is_excluded(fpath : str) -> bool:
        excluded_patterns: list[str] = ['.*\\.pyc', '.*/__pycache__', '.*\\.egg-info',
                                        '.*/.venv', '.*.git.*', '.*\\.idea.*', '.*build.*']

        regex_patterns = [re.compile(pattern) for pattern in excluded_patterns]
        matches_exclusion = any([pattern.match(fpath) for pattern in regex_patterns])
        return matches_exclusion

    # ---------------------------------------------
    # Properties

    def get_fullname(self) -> str:
        symbol = '🗎' if os.path.isfile(self.source_path) else '🗀'
        cond_backslash = '/' if os.path.isdir(self.source_path) else ''
        return f'{symbol} {self.name}{cond_backslash}'

    def get_name(self) -> str:
        return os.path.basename(self.source_path)

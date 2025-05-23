import os
from typing import Optional

from holytools.fsys import Directory, File


class DecoratedDirectory(Directory):
    def get_tree(self, desc_map : Optional[dict[str,str]] = None, path_to_fileID : Optional[dict[str, int]] = None,
                       indent : int = 0, max_children : int = 10, *args, **kwargs) -> str:
        if desc_map is None:
            desc_map = {}
        if path_to_fileID is None:
            path_to_fileID = {}

        indentation = '\t' * indent
        cond_desc = f'\n{desc_map[self.get_path()]}' if self.get_path() in desc_map else ""
        total_str = (f'{indentation}🗀 {self.get_name()}/'
                     f'{cond_desc}')

        subpaths = [os.path.join(self.get_path(), name) for name in os.listdir(self.get_path())]
        files = [File(path=p) for p in subpaths if os.path.isfile(p)]
        directories = [DecoratedDirectory(path=p) for p in subpaths if os.path.isdir(p)]

        for node in files + directories:
            cond_fileid = f' | FileID = {path_to_fileID[node.get_path()]}' if node.get_path() in path_to_fileID else ''
            total_str += f'\n{node.get_tree(indent=indent + 1, max_children=max_children)}{cond_fileid}'
        return total_str

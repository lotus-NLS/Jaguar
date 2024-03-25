import os
from typing import Optional
from PIL.Image import Image as PILImage
from engine.l4_tools import InvalidArgValue
from hollarek.fsys import FsysNode
from hollarek.abstract import Tree
from .workspace import Workspace

# ---------------------------------------------------------

class LotusFileExplorer(Workspace):
    def __init__(self):
        super().__init__()
        self.current_dir_path: Optional[str] = None

    def on_open(self, directory_path: str = '~'):
        """Opens the file explorer in the specified directory"""
        self.cd(directory_path=directory_path)

    def on_close(self):
        """Close LotusFileExplorer"""
        self.current_dir_path = None

    def cd(self, directory_path : str):
        """Change the directory"""
        new_dirpath = os.path.expanduser(directory_path)
        if not os.path.isabs(directory_path):
            new_dirpath = os.path.join(self.current_dir_path, new_dirpath)
        if not os.path.isdir(new_dirpath):
            raise InvalidArgValue(f'Invalid directory path: {new_dirpath} is not a directory')
        self.current_dir_path = new_dirpath

    # ---------------------------------------------------------
    # context

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_text(self) -> str:
        from devtools import Timer
        timer = Timer()
        timer.start()
        node = FsysNode(self.current_dir_path)

        subtrees = []
        max_size = 100
        for child in node.get_child_nodes():
            try:
                tree = child.get_tree(max_size=max_size)
            except:
                name_with_warning = f'{child.get_name()} [Warning: Directory too large; Exceeds limit of {max_size} files/folders]'
                tree = Tree({ name_with_warning : {}})
            subtrees.append(tree)

        tree = Tree.join_trees(root=node, subtrees=subtrees)
        content = f'[Directory: {self.current_dir_path}]\n {tree.as_str()}'
        timer.capture()
        return content

    @classmethod
    def get_desc(cls) -> str:
        return "A file explorer to navigate and display file structures"

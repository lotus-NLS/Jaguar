import os
from typing import Optional
from PIL.Image import Image as PILImage
from engine.l4_tools import InvalidArgValue
from hollarek.fsys import FsysNode
from .workspace import Workspace
from devtools import Timer
# ---------------------------------------------------------

class LotusFileExplorer(Workspace):
    def __init__(self):
        super().__init__()
        self.current_dir: Optional[str] = None

    def on_open(self, workdir_path: str = '~'):
        """Opens the file explorer in the specified working directory"""
        cwd = os.path.expanduser(workdir_path)
        if not os.path.isdir(cwd):
            raise InvalidArgValue(f'Invalid directory path: {cwd} is not a directory')
        self.current_dir = cwd

    def on_close(self):
        """Close LotusFileExplorer"""
        self.current_dir = None

    # ---------------------------------------------------------
    # context

    def get_image(self) -> Optional[PILImage]:
        return None

    def get_text(self) -> str:
        timer = Timer()
        timer.start()
        node = FsysNode(self.current_dir)
        content = f'[Current directory: {self.current_dir}]\n {node.get_tree()}'
        timer.capture()
        return content

    @classmethod
    def get_desc(cls) -> str:
        return "A file explorer to navigate and display file structures"

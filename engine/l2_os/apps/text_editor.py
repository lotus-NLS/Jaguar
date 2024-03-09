from __future__ import annotations
from typing import Optional

from PIL.Image import Image as PILImage
from hollarek.fsys import FsysNode

from engine.l2_os.application import Tab

# ---------------------------------------------------------

class TextTab(Tab):
    def __init__(self, uri : str):
        super().__init__(uri=uri)
        self.fpath : str = uri
        self.content : Optional[str] =None

    def get_text(self) -> Optional[str]:
        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
        msg = ''.join(numbered_lines)
        return msg


    def get_image(self) -> Optional[PILImage]:
        return None


    def insert(self, line: int, content: str):
        if FsysNode(path=self.fpath).get_suffix() == 'pdf':
            raise ValueError('Cannot edit pdf files')
        if line <= 0:
            raise ValueError("Line number must be a positive integer.")

        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        index = line - 1
        lines.insert(index, content)

        with open(self.fpath, 'w') as f:
            f.writelines(lines)
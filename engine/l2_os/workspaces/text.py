from __future__ import annotations

from typing import Optional
from PIL.Image import Image as PILImage

from hollarek.file import TextFile
from .workspace import Workspace
# ---------------------------------------------------------

class LotusText(Workspace):
    def __init__(self):
        super().__init__()
        self.content : Optional[str] = None
        self.text_file : Optional[TextFile] = None

    def open(self, filepath : str):
        self.text_file = TextFile(fpath=filepath, require_writable=True)

    def close(self, *args, **kwargs):
        pass

    def get_text(self) -> str:
        try:
            text = self.text_file.read()
            lines = text.splitlines()
        except:
            lines = ['']

        numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
        msg = ''.join(numbered_lines)
        return msg

    def get_image(self) -> Optional[PILImage]:
        return None

    # ---------------------------------------------------------

    def insert(self, line: int, content: str):
        if line <= 0:
            raise ValueError("Line number must be a positive integer.")
        try:
            text = self.text_file.read()
            lines = text.splitlines()
        except:
            lines = []
        index = line - 1
        lines.insert(index, content)

        text = '\n'.join(lines)
        self.text_file.write(content=text)


    def delete_lines(self, start_line: int, end_line: int):
        if start_line <= 0 or end_line < start_line:
            raise ValueError("Invalid line range.")

        lines = self.text_file.read()
        del lines[start_line - 1:end_line]
        newcontent = '\n'.join(lines)
        self.text_file.write(newcontent)

from __future__ import annotations

import os.path
from typing import Optional
from PIL.Image import Image as PILImage

from hollarek.file import TextFile
from .workspace import Workspace
# ---------------------------------------------------------

class LotusText(Workspace):
    def __init__(self, filepath : str):
        super().__init__()
        self.content : Optional[str] = None
        self.fpath = filepath
        self.text_file : TextFile = TextFile(fpath=filepath, require_writable=True)


    def get_text(self) -> Optional[str]:
        if not os.path.isfile(self.fpath):
            return ''

        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
        msg = ''.join(numbered_lines)
        return msg


    def get_image(self) -> Optional[PILImage]:
        return None


    def insert(self, line: int, content: str):
        if self.text_file.get_suffix() == 'pdf':
            raise ValueError('Cannot edit pdf files')
        if line <= 0:
            raise ValueError("Line number must be a positive integer.")

        try:
            with open(self.fpath, 'r') as f:
                lines = f.readlines()
        except:
            lines = []
        index = line - 1
        lines.insert(index, content)
        with open(self.fpath, 'w') as f:
            f.writelines(lines)


    def delete_lines(self, start_line: int, end_line: int):
        if self.text_file.get_suffix().lower() == 'pdf':
            raise ValueError('Cannot edit pdf files')
        if start_line <= 0 or end_line < start_line:
            raise ValueError("Invalid line range.")

        with open(self.fpath, 'r') as f:
            lines = f.readlines()
        del lines[start_line - 1:end_line]
        with open(self.fpath, 'w') as f:
            f.writelines(lines)

    @classmethod
    def get_desc(cls) -> str:
        return (f'This application allows you to view almost any text file including .pdf and .docx files'
                f'However you can only edit plain text files')
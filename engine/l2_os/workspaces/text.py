from __future__ import annotations

import os.path
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
        """If file exists will provide a view. It it doesn't exists will attempt to create a pathtext file at filepath"""
        self.text_file = TextFile(fpath=filepath, require_writable=True)


    def close(self, *args, **kwargs):
        """Closes LotusText. Once closed you can open another file"""
        pass

    # ---------------------------------------------------------
    # actions

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

    # ---------------------------------------------------------
    # context

    def get_text(self) -> str:
        fpath = self.text_file.fpath
        meta =  f'Currently editing file: \"{fpath}\"\n'
        meta += f'File exists on disk: \"{os.path.isfile(fpath)}\"\n'

        try:
            content = self.text_file.read()
            lines = content.splitlines()
        except:
            lines = ['']

        numbered_lines = [f"{i + 1} | {line}" for i, line in enumerate(lines)]
        labeled_content = '\n'.join(numbered_lines)
        return meta + labeled_content

    def get_image(self) -> Optional[PILImage]:
        return None

    @classmethod
    def get_desc(cls) -> str:
        return ("Allows for viewing *any* file containing text including pdf, csv, doc, docx and "
                "even handwritten text in .jpg. Can only write to plaintext files.")


from __future__ import annotations

import os.path
from typing import Optional

from PIL.Image import Image as PILImage
from holytools.fileIO import PlaintextFile

from .workspace import Workspace


# ---------------------------------------------------------


class DocumentEditor(Workspace):
    def __init__(self):
        super().__init__()
        self.content : Optional[str] = None
        self.text_file : Optional[PlaintextFile] = None

    def open(self, filepath : str, require_writable : bool = False):
        """Allowd you to view and edit plain Text files. A view-only mode allows for also viewing text in .pdfs, .doc, .docx and even handwritten text in .jpg and .png images """
        self.text_file = PlaintextFile(fpath=filepath, require_writable=require_writable)
        if self.text_file.exists_on_disk():
            self.text_file.read() # one test run to check if the file can be read

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

        content = self.text_file.read()
        lines = content.splitlines()

        del lines[start_line - 1:end_line]
        newcontent = '\n'.join(lines)
        self.text_file.write(newcontent)

    # ---------------------------------------------------------
    # context

    def get_text(self) -> str:
        fpath = self.text_file.fpath
        exists_on_disk = os.path.isfile(fpath)
        meta =  f'Currently editing file: \"{fpath}\"\n'
        meta += f'File exists on disk: \"{exists_on_disk}\"\n'

        if exists_on_disk:
            content = self.text_file.read()
            lines = content.splitlines()
        else:
            lines = []

        highest_line_number = len(lines)
        min_space = len(str(highest_line_number))+1
        numbered_lines = [f"{i + 1:<{min_space}}| {line}" for i, line in enumerate(lines)]
        labeled_content = '\n'.join(numbered_lines)
        return meta + labeled_content

    def get_image(self) -> Optional[PILImage]:
        return None

    @classmethod
    def get_desc(cls) -> str:
        return ("Allows for viewing *any* file containing text including pdf, csv, doc, docx and "
                "even handwritten text in .jpg. Can only write to Plaintext files.")


from __future__ import annotations
import os
from enum import Enum

from hollarek.io import get_text, TextFileType
from engine.l3_tools.tool import Tool, ToolArg
from engine.l3_tools import Phase
from hollarek.io.fsys import FsysNode

# ---------------------------------------------------------

class Mode(Enum):
    WRITE = 'write'
    READ = 'read'

    @classmethod
    def modes_as_str_list(cls) -> list[str]:
        return [cls.WRITE.value, cls.READ.value]


class FileIO(Tool):
    def __init__(self):
        super().__init__()
        self.desc = f'Read or write plain text or pdfs files'

        self.mode_arg : ToolArg = ToolArg(name='mode', choices=Mode.modes_as_str_list())
        self.fpath_arg : ToolArg = ToolArg(name='fpath', desc='Filepath to be read or written to')
        self.content_arg : ToolArg = ToolArg(name='content', desc='text to write for write mode only', is_optional=True)


    def do(self):
        location = os.path.expanduser(self.fpath_arg.val)
        mode = Mode(self.mode_arg.val)

        if mode == Mode.WRITE:
            content = self.content_arg.val
            self.do_write(location,content)

        if mode == Mode.READ:
            self.do_read(location)


    def do_write(self, location: str, content: str):
        try:
            with open(location, 'w') as file:
                file.write(content)
                self.log(f'Suceeded in writing out file', phase=Phase.UPDATE)

        except Exception:
            self.log(f'An error occured while trying to write file', phase=Phase.EXCEPTION)


    def do_read(self, fpath : str):
        if not os.path.isfile(fpath):
            raise FileNotFoundError(f'There is no file located at given location {fpath}. Aborting ...')

        suffix = FsysNode(path=fpath).get_suffix()
        self.log(f'Attempting to read file located at {fpath}', phase=Phase.UPDATE)
        file_type = TextFileType.PDF if suffix == 'pdf' else TextFileType.PLAINTEXT
        file_content = get_text(fpath=fpath,file_type=file_type)
        self.log(f'File content:\n{file_content}', phase=Phase.UPDATE)



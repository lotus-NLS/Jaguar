from __future__ import annotations
import os
from hollarek.io import get_text, TextFileType

from engine.l3_tools.m1_tooldef.tool import Tool
from engine.l1_agent.agent.tool_handler import ToolArg

# ---------------------------------------------------------

class FILE_IO(Tool):
    read = 'read'
    write = 'write'

    modes = [read,write]
    file_types = [TextFileType.PDF.value, TextFileType.PLAINTEXT.value]

    def __init__(self):
        super().__init__()
        self.desc = f'Read or write text files based on mode'

        self.mode_arg : ToolArg = self.create_arg(
            name='mode', dtype=str,
            desc='',
            available_options=FILE_IO.modes)

        self.fpath_arg : ToolArg = self.create_arg(
            name='fpath', dtype=str,
            desc='Filepath to be read or written to')

        self.format_arg : ToolArg = self.create_arg(
            name='file_format', dtype=str,
            available_options=FILE_IO.file_types,
            desc=f'read mode only')

        self.content_arg: ToolArg = self.create_arg(name='content', dtype=str,
                                                    desc='text to write for write mode only')


    def do(self):
        location = os.path.expanduser(self.fpath_arg.val)
        mode = self.mode_arg.val

        if mode == FILE_IO.write:
            content = self.content_arg.val
            self.do_write(location,content)

        if mode == FILE_IO.read:
            self.do_read(location)


    def do_write(self, location: str, content: str):
        try:
            with open(location, 'w') as file:
                file.write(content)
                self.update_log(f'Suceeded in writing out file')

        except Exception:
            self.exception_log(f'An error occured while trying to write file')


    def do_read(self, fpath : str):
        if not os.path.isfile(fpath):
            self.semantic_error(f'There is no file located at given location {fpath}. Aborting ...')
            return

        chosen_format = self.format_arg.val
        if not self.format_arg.val in FILE_IO.file_types:
            self.semantic_error(f'Given format {chosen_format} is not an allowed format. Please choose a format from {self.file_types}')
            raise IOError

        try:
            file_type = TextFileType.PLAINTEXT if self.format_arg.val == TextFileType.PLAINTEXT.value else TextFileType.PDF
            self.update_log(f'Attempting to read file located at {fpath}')
            file_content = get_text(fpath=fpath,file_type=file_type)
            self.update_log(f'File content:\n{file_content}')

        except Exception:
            self.exception_log(f'An exception occured while trying to read the file located at {fpath}\n')


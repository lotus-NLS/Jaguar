from __future__ import annotations
import os
from engine.l2_lotus_agent.m0_agent.tool_handler import ToolArg
from engine.pyutils import get_pdf_file_content, get_txt_file_content

from engine.l1_lotus_tools.m0_toolbox.tool import Tool


# ---------------------------------------------------------

class FILE_IO(Tool):
    read = 'read'
    write = 'write'

    modes = [read,write]

    text_format = 'txt'
    pdf_format = 'pdf'
    allowed_formats = [text_format,pdf_format]

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
            available_options=[FILE_IO.text_format, FILE_IO.pdf_format],
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


    def do_read(self, location : str):
        if not os.path.isfile(location):
            self.semantic_error(f'There is no file located at given location {location}. Aborting ...')
            return

        chosen_format = self.format_arg.val
        if not self.format_arg.val in [FILE_IO.text_format, FILE_IO.pdf_format]:
            self.semantic_error(f'Given format {chosen_format} is not an allowed format. Please choose a format from {self.allowed_formats}')

        retrieval_function = get_txt_file_content if chosen_format == self.text_format else get_pdf_file_content

        try:
            self.update_log(f'Attempting to read file located at {location}')
            file_content = retrieval_function(location=location)
            self.update_log(f'File content:\n{file_content}')

        except Exception:
            self.exception_log(f'An exception occured while trying to read the file located at {location}\n')

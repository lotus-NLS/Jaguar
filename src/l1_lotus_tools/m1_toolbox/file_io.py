from __future__ import annotations
import os
from PyPDF2 import PdfReader

from src.l1_lotus_tools.m0_tool_class.tool import ToolArg, Tool

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
        self.desc = f'The {self.name} has two modes, allows you to read the contents of a plain text file or a pdf.'

        self.mode_arg : ToolArg = self.create_arg(
            name='mode', dtype=str,
            desc='',
            available_options=FILE_IO.modes)

        self.fpath_arg : ToolArg = self.create_arg(
            name='fpath', dtype=str,
            desc='Filepath of file to be read or written')

        # TODO 0.4: It should not be the task of the agent to decide the format.
        # TODO 0.4: The tool itself should pick the appropriate read function
        self.format_arg : ToolArg = self.create_arg(
            name='file_format', dtype=str,
            available_options=[FILE_IO.text_format, FILE_IO.pdf_format],
            is_optional=False,
            desc=f'READ mode only: This is the format of the file you want to read')

        self.content_arg: ToolArg = self.create_arg(name='content', dtype=str,
                                                    desc='The content that will be written to the file')

    def do(self) -> None:
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

        retrieval_function = self.get_txt_file_content if chosen_format == self.text_format else self.get_pdf_file_content

        try:
            self.update_log(f'Attempting to read file located at {location}')
            file_content = retrieval_function(location=location)
            self.update_log(f'File content:\n{file_content}')

        except Exception:
            self.exception_log(f'An exception occured while trying to read the file located at {location}\n')


    @staticmethod
    def get_txt_file_content(location : str) -> str:
        with open(location, 'r') as file:
            file_content = file.read()
        return file_content


    @staticmethod
    def get_pdf_file_content(location : str) -> str:
        pdf_file = open(location, 'rb')
        pdf_reader = PdfReader(pdf_file)

        pdf_content = ''
        for page_num in range(len(pdf_reader.pages)):
            pdf_content += pdf_reader.pages[page_num].extract_text()

        # Close the PDF file
        pdf_file.close()

        return pdf_content

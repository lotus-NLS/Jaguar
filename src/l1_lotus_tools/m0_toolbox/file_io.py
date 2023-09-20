import os
from PyPDF2 import PdfReader
from src.l2_lotus_core.m0_agent.tool import Tool, ToolArg

# ---------------------------------------------------------


class READ(Tool):
    text_format = 'txt'
    pdf_format = 'pdf'
    allowed_formats = [text_format,pdf_format]

    def __init__(self):
        super().__init__()
        self.description = 'The READ tool allows you to read the contents of a plain text file or a pdf.'

        self.fpath_arg : ToolArg = self.create_arg(
            name='fpath', dtype=str,
            desc='This is the path to the file which you will read')

        self.format_arg : ToolArg = self.create_arg(
            name='file_format', dtype=str,
            available_options=[READ.text_format,READ.pdf_format],
            desc=f'This is the format of the file you want to read')


    def do(self) -> None:
        location = self.fpath_arg.val

        if not os.path.isfile(location):
            self.semantic_error(f'There is no file located at given location {location}. Aborting ...')
            return

        chosen_format = self.format_arg.val
        if not self.format_arg.val in [READ.text_format, READ.pdf_format]:
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


class WRITE(Tool):
    def __init__(self):
        super().__init__()
        self.description = 'The WRITE tool allows you to write content to a text file on your system'

        self.fpath_arg : ToolArg = self.create_arg(name='fpath', dtype=str,
                                                   desc='The path of the file that you will write')

        self.content_arg : ToolArg = self.create_arg(name='content', dtype=str,
                                                     desc='The content that will be written to the file')

    def do(self):
        location = self.fpath_arg.val

        try:
            with open(location, 'w') as file:
                file.write(self.content_arg.val)
                self.update_log(f'Suceeded in writing out file')

        except Exception as e:
            self.exception_log(f'An error occured while trying to write file: {e}')

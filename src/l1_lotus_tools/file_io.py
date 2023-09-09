import os
from PyPDF2 import PdfReader
from src.l2_lotus_core.m1_models.tool import Tool, ToolArg

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
            desc=f'This is the format of the file you want to read.'
                        f'Enter {self.text_format} for a text file or {self.pdf_format} for a pdf')


    def do(self) -> None:
        location = self.fpath_arg.val

        if not os.path.isfile(location):
            self.error_log(f'There is no file located at given location {location}')

        chosen_format = self.format_arg.val
        if not self.format_arg.val in [self.text_format, self.pdf_format]:
            self.error_log(f'Given format {chosen_format} is not an allowed format.\n'
                           f'Please choose a format from {self.allowed_formats}')


        if chosen_format == self.text_format:
            get_content_action = self.get_txt_file_content
        else:
            get_content_action = self.get_pdf_file_content

        try:
            self.progress_log(f'Attempting to read file located at {location}')
            file_content = get_content_action(location=location)
            self.progress_log(f'Read file content:\n{file_content}\n'
                              f'Successfully completed reading of file.')

        except Exception:
            self.error_log(f'An error occured while trying to read the file located at {location}\n')

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
        self.description = 'The WRITE tool allows you to write content to a file on the user system'

        self.fpath_arg : ToolArg = self.create_arg(name='fpath', dtype=str,
                                                   desc='The path of the file that you will write')

        self.content_arg : ToolArg = self.create_arg(name='content', dtype=str,
                                                     desc='The content that will be written to the file')

    def do(self):
        location = self.fpath_arg.val

        parent_dir = os.path.dirname(location)
        if os.access(parent_dir,os.W_OK):
            self.error_log(f'{parent_dir} is not a writable directory')

        try:
            with open(self.fpath_arg.val, 'w') as file:
                file.write(self.content_arg.val)
                self.progress_log(f'Suceeded in writing out file')

        except Exception as e:
            self.error_log(f'An error occured while trying to write file: {e}')

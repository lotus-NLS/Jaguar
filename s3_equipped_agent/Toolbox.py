import os
import traceback
from s2_agent.Tool import Tool,ToolArg
from PyPDF2 import PdfReader


# Tool class logging
# -> [START] : For tool launch
# -> [FINISH]: Tool done

# Specifc tool implementations (READ, WRITE etc.) logging:
# -> [PROGRESS] : For updates on tool progress
# -> [ERROR] : For reporting encountered errors if any

# NOTE : the name 'format' for an arugment seems to be a built in keyword which results in an error
# NOTE : -> Do not use the name 'format' for arguments
# ---------------------------------------------------------


class READ(Tool):

    text_format = 'txt'
    pdf_format = 'pdf'
    allowed_formats = [text_format,pdf_format]

    def __init__(self):
        super().__init__()
        self.description = 'The READ tool allows you to read the contents of a text file or a pdf.'

        self.fpath_arg : ToolArg = self.create_argument(
            name='fpath', dtype=str,
            description='This is the path to the file which you will read')

        self.format_arg : ToolArg = self.create_argument(
            name='file_format', dtype=str,
            description=f'This is the format of the file you want to read.'
                        f'Enter {self.text_format} for a text file or {self.pdf_format} for a pdf')


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
            pdf_content += pdf_reader.pages[page_num].extractText()

        # Close the PDF file
        pdf_file.close()

        return pdf_content

    def do(self) -> None:
        location = self.fpath_arg.val

        if not os.path.isfile(location):
            self.log(f'[ERROR]: There is no file located at given location {location}')

        chosen_format = self.format_arg.val
        if not self.format_arg.val in [self.text_format, self.pdf_format]:
            self.log(f'[ERROR]: Given format {chosen_format} is not an allowed format.'
                     f' Please choose a format from {self.allowed_formats}')


        if chosen_format == self.text_format:
            get_content_action = self.get_txt_file_content
        else:
            get_content_action = self.get_pdf_file_content

        try:
            self.log(f'[PROGRESS]: Attempting to read file located at {location}')
            file_content = get_content_action(location=location)
            self.log(f'[PROGRESS]: {file_content}')
            self.log(f'[PROGRESS]: Successfully completed reading of file.')

        except Exception as e:
            self.log(f'[ERROR]: An error occured while trying to read the file located at {location}')
            self.log(f'[ERROR]: {traceback.format_exc()}')


class WRITE(Tool):
    def __init__(self):
        super().__init__()
        self.description = 'The WRITE tool allows you to write content to a file on the user system'

        self.fpath_arg : ToolArg = self.create_argument(name='fpath', dtype=str,
                                                 description='The path of the file that you will write')

        self.content_arg : ToolArg = self.create_argument(name='content',dtype=str,
                                                description='The content that will be written to the file')

    def do(self):
        location = self.fpath_arg.val

        parent_dir = os.path.dirname(location)
        if os.access(parent_dir,os.W_OK):
            self.log(f'[ERROR]: {parent_dir} is not a writable directory')

        try:
            with open(self.fpath_arg.val, 'w') as file:
                file.write(self.content_arg.val)
                self.log(f'[PROGRESS]: Suceeded in writing out file')

        except:
            self.log(f'[ERROR]: An error occured while trying to write file')


# class UPDATE_DIRECTIVE(Tool):
#     def __init__(self, Directive):
#         super().__init__()
#
#     def do(self):
#         pass


basic_tools = [READ(),WRITE()]


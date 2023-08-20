# from typing import Callable
# from typing import List
import os
from s2_agent.Tool import Tool,ToolArg


# TOOL LOGGING Protocol:
# -> [START] : For tool launch
# -> [PROGRESS] : For updates on tool progress
# -> [RESULT] : For what the tool retrieved if applicable
# -> [ERROR] : For reporting encountered errors if any
# -> [FINISH]: Tool done

# ---------------------------------------------------------


class Toolbox:

    # class SAY(Tool):
    #     def __init__(self):
    #         super().__init__()
    #         self.description = 'Say hello to the guests we have in our home today via a message board '
    #
    #         self.text_argument : ToolArg = self.create_argument(name='text_content', dtype=str,
    #                                                   description='This is what you will say to the guests')
    #
    #     def do(self):
    #         self.log(f'**** {self.text_argument.val} ****')


    class READ(Tool):
        def __init__(self):
            super().__init__()
            self.description = 'The READ tool allows you to read the contents of a file.'

            self.fpath_arg : ToolArg = self.create_argument(name='fpath', dtype=str,
                                                     description='This is the path to the file which you will read')


        def do(self):
            location = self.fpath_arg.val

            if not os.path.isfile(location):
                self.log(f'[ERROR]: There is no file located at given location {location}')

            try:
                self.log(f'[PROGRESS]: Attempting to read file located at {location}')
                with open(location, 'f') as file:
                    file_content = file.read()
                    self.log(f'[RESULT]: {file_content}')
                    self.log('[PROGRESS]: Successfully completed reading of file.')

            except:
                self.log(f'[ERROR]: An error occured while trying to read the file located at {location}')


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


basic_tools = [Toolbox.READ(),Toolbox.WRITE()]


import os
print(os.access('/home/aiproj/pyWriter/s4_UI/run_GUddI.py',os.W_OK))

path = '/home/aiproj/pyWriter/s4_UI/run_GUddI.py'

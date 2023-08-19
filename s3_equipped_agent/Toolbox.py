# from typing import Callable
# from typing import List
import os
from s2_agent.Tool import Tool,ToolArg


# TOOL LOGGING Protocol:
# -> 1: Log launch of tool using "[START]"
# -> 2: If applicable log result of tool e.g. for READ file using [RESULT]
# -> 3: If log success or error of tool using [SUCCESS] or [ERROR]


# TOOL ERROR Catching
# -> Any possible fatal error must be caught in handle_call

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
                with open(location, 'f') as file:
                    file_content = file.read()
                    self.log(file_content)
                    self.log('Successfully completed reading of file.')

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

        # TODO Catch specfic errors
        def do(self):
            with open(self.fpath_arg.val, 'w') as file:
                file.write(self.content_arg.val)


    # class UPDATE_DIRECTIVE(Tool):
    #     def __init__(self, Directive):
    #         super().__init__()
    #
    #     def do(self):
    #         pass


basic_tools = [Toolbox.READ(),Toolbox.WRITE()]

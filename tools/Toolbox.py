# from typing import Callable
# from typing import List
import os
from tools.Argument import Arg


# TOOL LOGGING Protocol:
# -> 1: Log launch of tool using "[START]"
# -> 2: If applicable log result of tool e.g. for READ file using [RESULT]
# -> 3: If log success or error of tool using [SUCCESS] or [ERROR]


# TOOL ERROR Catching
# -> Any possible fatal error must be caught in handle_call

# ------------------------------------------------

class Tool:
    arguments = []

    def __init__(self):
        self.name = ''
        self.description : str = ''
        self.external_log = None
        self.arguments = []

    def create_argument(self, name: str, dtype: type, description: str):
        this_arg = Arg(name, dtype, description)
        self.arguments.append(this_arg)
        return this_arg

    def get_usage_instructions(self):
        tool_doc = {
            'name': f'{self.name}',
            'description': f'{self.description}',
            'parameters': {
                'type': 'object',
                'properties': {}
            }
        }

        for arg in self.arguments:
            tool_doc['parameters']['properties'][arg.name] = arg.generate_argument_doc()

        return tool_doc

    def log(self,to_log):
        log_text = f'{self.name} [TOOL LOGGER]: \n'
        log_text += '\"\n'
        log_text += to_log
        log_text += '"\n'

        if self.external_log is None:
            print(to_log)
        else:
            print(to_log)
            self.external_log(to_log)


    def handle_call(self, args_dict : dict):
        self.log(f'[START]: Attempting to launch tool {self.name}')

        arg_names = [arg.name for arg in self.arguments]
        arguments_included = all([arg in args_dict.keys() for arg in arg_names])

        if not arguments_included:
            self.log(f'[ERROR]: Call failed since provided dictionary {args_dict}'
                     f' did not cover all required tool arguments')
            return

        for arg in self.arguments:
            arg.val = args_dict[arg.name]

        try:
            self.log(f'[PROGRESS]: Tool {self.name} has been launched')
            self.do()
        except:
            self.log(f'[ERROR]: The Tool {self.name} encountered an error during execution. Aborting ...')


    def do(self):
        pass


class Toolbox:
    # DEBUG
    class SAY(Tool):
        def __init__(self):
            super().__init__()
            self.name = 'say_hi'
            self.description = 'Say hello to the guests we have in our home today via a message board '

            self.text_argument = self.create_argument(name='text_content', dtype=str,
                                                      description='This is what you will say to the guests')

        def do(self):
            self.log(f'**** {self.text_argument.val} ****')


    class READ(Tool):
        def __init__(self):
            super().__init__()
            self.name = 'say_hi'
            self.description = 'The READ tool allows you to read the contents of a file.'

            self.fpath_arg = self.create_argument(name='fpath', dtype=str,
                                                     description='This is the path to the file which you will read')

        def do(self):
            location = self.fpath_arg.val

            if not os.path.isfile(location):
                self.log(f'[ERROR]: There is no file located at given location {location}')

            try:
                with open(location, 'f') as file:
                    file_content = file.read()
                self.log('Successfully completed reading of file.')

                return file_content
            except:
                self.log(f'[ERROR]: An error occured while trying to read the file located at {location}')


    class WRITE(Tool):
        def __init__(self):
            super().__init__()
            self.name = 'say_hi'
            self.description = 'The WRITE tool allows you to write content to a text file on the user system'

            self.fpath_arg = self.create_argument(name='fpath', dtype=str,
                                                     description='The path of the file that you will write')

            self.content_arg = self.create_argument(name='content',dtype=str,
                                                    description='The content that will be written to the file')

        # TODO Catch specfic errors
        def do(self):
            with open(self.fpath_arg.val, 'w') as file:
                file.write(self.content_arg.val)

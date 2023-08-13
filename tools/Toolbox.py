# from typing import Callable
# from typing import List
from tools.Argument import Arg

# ------------------------------------------------

class Tool:
    arguments = []

    def __init__(self):
        self.name = None
        self.description = None
        self.external_log = None
        self.arguments = []

    def create_argument(self, name: str, dtype: type, description: str):
        this_arg = Arg(name, dtype, description)
        self.arguments.append(this_arg)
        return this_arg

    def get_tool_info(self):
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
        if self.external_log is None:
            print(to_log)
        else:
            print(to_log)
            self.external_log(to_log)


    def handle_call(self, any_dict : dict):
        arg_names = [arg.name for arg in self.arguments]
        arguments_included = all([arg in any_dict.keys() for arg in arg_names])

        if not arguments_included:
            self.log(f'[ERROR]: Call failed since provided dictionary {any_dict}'
                     f' did not cover all required tool arguments')
            return

        for arg in self.arguments:
            arg.val = any_dict[arg.name]
        self.do()

    def do(self):
        pass



class Toolbox:
    # DEBUG
    class Say_hi(Tool):
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
            with open(self.fpath_arg.val, 'f') as file:
                file_content = file.read()

            self.log('Successfully completed reading of file.')
            return file_content


    class WRITE(Tool):
        def __init__(self):
            super().__init__()
            self.name = 'say_hi'
            self.description = 'The WRITE tool allows you to write content to a text file on the user system'

            self.fpath_arg = self.create_argument(name='fpath', dtype=str,
                                                     description='The path of the file that you will write')

            self.content_arg = self.create_argument(name='content',dtype=str,
                                                    description='The content that will be written to the file')

        def do(self):
            with open(self.fpath_arg.val, 'w') as file:
                file.write(self.content_arg.val)

# from typing import Callable
# from typing import List
from tools.Argument import Arg

# ------------------------------------------------

class Tool:
    arguments = []

    def __init__(self):
        self.name = None
        self.description = None
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

    def handle_call(self, any_dict : dict):
        arg_names = [arg.name for arg in self.arguments]
        arguments_included = all([arg in any_dict.keys() for arg in arg_names])

        # TODO: Have to provide feeback about what was wrong about the call
        if not arguments_included:
            print(f'[ERROR]: Call failed since provided dictionary {any_dict}'
                  f' did not cover all required tool arguments')
            return

        for arg in self.arguments:
            arg.val = any_dict[arg.name]
        self.do()

    def do(self):
        pass



# TODO: The Tools have to log out feedback to the agent that calls it. Probably they will need to receive a
# logger function from the agent.

class Toolbox:
    # TODO: Maybe tool_list is not needed and I should simply define tool lists for the agents themselves?
    # TODO: This would detangle things more and after all maybe not all agents should even have the same permissions?
    tool_list = []

    # DEBUG
    class Say_hi(Tool):
        def __init__(self):
            super().__init__()
            self.name = 'say_hi'
            self.description = 'Say hello to the guests we have in our home today via a message board '

            self.text_argument = self.create_argument(name='text_content', dtype=str,
                                                      description='This is what you will say to the guests')

        def do(self):
            print(f'**** {self.text_argument.val} ****')


    class READ(Tool):
        def __init__(self):
            super().__init__()
            self.name = 'say_hi'
            self.description = 'The READ tool allows you to read the contents of a file.'

            self.fpath_arg = self.create_argument(name='fpath', dtype=str,
                                                     description='This is the path to the file which you will read')

        def do(self):
            with open(self.fpath_arg.val, 'f') as file:
                return file.read()


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

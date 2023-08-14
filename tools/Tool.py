class Tool_arg:
    def __init__(self, name: str, dtype : type, description: str, value = None):
        self.name = name
        self.dtype = dtype
        self.description = description
        self.val = value

    def generate_argument_doc(self):
        arg_doc = {
            self.name: {
                'type': f'{self.dtype}',
                'description': f'{self.description}'
            }
        }
        return arg_doc


class Tool:
    arguments = []

    def __init__(self):
        self.name = self.__class__.__name__
        self.name = ''
        self.description : str = ''
        self.external_log = None
        self.arguments = []

    def create_argument(self, name: str, dtype: type, description: str):
        this_arg = Tool_arg(name, dtype, description)
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

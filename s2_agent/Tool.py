from typing import Callable

class ToolArg:
    def __init__(self, name: str, dtype : type, description: str, value = None):
        self.name : str = name
        self.dtype : type = dtype
        self.description : str = description
        self.val : dtype = value

    def get_arg_json_doc(self):
        arg_doc = {
            self.name: {
                'type': f'{self.dtype}',
                'description': f'{self.description}'
            }
        }
        return arg_doc


# TODO: Create loggers for different logging types
class Tool:
    def __init__(self):
        self.name : str = self.__class__.__name__
        self.description : str = ''
        self.external_log : Callable = lambda *args, **kwargs: None
        self.arguments : list[ToolArg] = []


    def create_argument(self, name: str, dtype: type, description: str) -> ToolArg:
        this_arg = ToolArg(name, dtype, description)
        self.arguments.append(this_arg)
        return this_arg


    def get_tool_json_doc(self) -> dict[str, str]:
        tool_doc = {
            'name': f'{self.name}',
            'description': f'{self.description}',
            'parameters': {
                'type': 'object',
                'properties': {}
            }
        }

        for arg in self.arguments:
            tool_doc['parameters']['properties'][arg.name] = arg.get_arg_json_doc()

        return tool_doc


    def log(self,to_log : str):
        # log_text = f'{self.name} [TOOL LOGGER]: {to_log}'
        log_text = f'## Internal Assistant log:{to_log}'

        if self.external_log is None:
            print(log_text)
        else:
            self.external_log(log_text)


    def handle_call(self, args_dict : dict):
        self.log(f'[START]: Attempting to launch tool {self.name} with args {args_dict}')

        arg_names = [arg.name for arg in self.arguments]
        arguments_included = all([arg in args_dict.keys() for arg in arg_names])

        if not arguments_included:
            self.log(f'[FINISH]: Call failed since provided dictionary {args_dict}'
                     f' did not cover all required tool arguments')
            return

        for arg in self.arguments:
            arg.val = args_dict[arg.name]

        try:
            self.log(f'[PROGRESS]: Tool {self.name} has been launched')
            self.do()
            self.log(f'[FINISH]: Tool {self.name} completed execution')
        except:
            self.log(f'[FINISH]: The Tool {self.name} encountered an unhandeled exception during execution. Aborting ...')


    def do(self):
        pass

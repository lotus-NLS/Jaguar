from typing import Callable


# Tool class logging
# -> [START] : For tool launch
# -> [FINISH]: Tool done

# Specifc tool implementations (READ, WRITE etc.) logging:
# -> [PROGRESS] : For updates on tool progress
# -> [ERROR] : For reporting encountered errors if any

# ---------------------------------------------------

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


    def handle_call(self, args_dict : dict):
        self.start_log(f'Attempting to launch tool {self.name} with args {args_dict}')

        arg_names = [arg.name for arg in self.arguments]
        arguments_included = all([arg in args_dict.keys() for arg in arg_names])

        if not arguments_included:
            self.finish_log(f'Call failed since provided dictionary {args_dict}'
                            f' did not cover all required tool arguments')
            return

        for arg in self.arguments:
            arg.val = args_dict[arg.name]

        try:
            self.progress_log(f'Tool {self.name} has been launched')
            self.do()
            self.finish_log(f'Tool {self.name} completed execution')
        except:
            self.finish_log(f'The Tool {self.name} encountered an unhandeled exception during execution. Aborting ...')


    def do(self):
        pass

    # ---------------------------------------------------
    # Logging

    def log(self, to_log: str):
        if self.external_log is None:
            print(to_log)
        else:
            self.external_log(to_log)

    def start_log(self, to_log):
        self.log(f'[Start]: {to_log}')

    def error_log(self, to_log):
        self.log(f'[Error]: {to_log}')

    def progress_log(self, to_log):
        self.log(f'[Progress]: {to_log}')

    def finish_log(self, to_log):
        self.log(f'[Finish]: {to_log}')


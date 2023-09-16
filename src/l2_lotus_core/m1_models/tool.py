from typing import Callable, Union, Optional
from typing import Any
import traceback

from func_timeout import func_timeout, FunctionTimedOut


# Tool class logging
# -> [START] : For tool launch
# -> [FINISH]: Tool done

# Specifc tool implementations (READ, WRITE etc.) logging:
# -> [PROGRESS] : For updates on tool progress
# -> [ERROR] : For reporting encountered errors if any

# ---------------------------------------------------

class ToolArg:
    def __init__(self, name: str, dtype : type, description: str,available_options : Optional[list[str]] = None):
        self.name : str = name
        self.dtype : type = dtype
        self.description : str = description
        self.val : dtype = None
        self.available_options: Optional[list[str]] = available_options

    def get_arg_json_doc(self) -> dict[str,str]:
        arg_doc = {
                'type': self.get_json_type(self.dtype),
                'description': f'{self.description}',
        }

        if not self.available_options is None:
            arg_doc['enum'] = self.available_options

        return arg_doc


    @staticmethod
    def get_json_type(python_type) -> Union[str,None]:
        # The 'array' type corresponding to dict and list, seem to break something on OpenAI end,
        # hence why I didn't include them; See logs (@ https://www.notion.so/pyWrite0-3-a53c1b16ef3646df9c141a144f8197a2)

        default_type = 'string'
        type_mapping = {
            int: "number",
            float: "number",
            str: "string",
            bool: "boolean",
            type(None): "null",
            dict: "object"
        }

        if python_type in type_mapping:
            json_type = type_mapping[python_type]
        else:
            json_type = default_type

        return json_type


class Tool:
    timout_in_sec = 60

    def __init__(self):
        self.name : str = self.__class__.__name__
        self.desc : str = ''
        self.external_log : Callable = lambda *args, **kwargs: None
        self.arguments : list[ToolArg] = []


    def create_arg(self, name: str, dtype: type, desc: str, available_options : Optional[list[str]] = None) -> ToolArg:
        this_arg = ToolArg(name, dtype, desc,available_options)
        self.arguments.append(this_arg)
        return this_arg


    def get_tool_json_doc(self) -> dict[str,Any]:
        tool_doc = {
            'name': f'{self.name}',
            'description': f'{self.desc}',
            'parameters': {
                'type': 'object',
                'properties': {}
            }
        }

        for arg in self.arguments:
            tool_doc['parameters']['properties'][arg.name] = arg.get_arg_json_doc()
        return tool_doc


    def handle_call(self, args_dict : dict) -> None:
        self.start_log(f'Attempting to launch tool {self.name} with args: {args_dict}')

        arg_names = [arg.name for arg in self.arguments]
        arguments_included = all([arg in args_dict.keys() for arg in arg_names])

        if not arguments_included:
            self.finish_log(f'Call failed since provided dictionary {args_dict} did not cover all required tool arguments')
            return

        for arg in self.arguments:
            arg.val = args_dict[arg.name]

        try:
            self.progress_log(f'Tool {self.name} has been launched')
            func_timeout(timeout=Tool.timout_in_sec, func= self.do)
            self.finish_log(f'Tool {self.name} completed execution')

        except FunctionTimedOut:
            self.finish_log(f'The tool {self.name} timed out without completing after {Tool.timout_in_sec} seconds. Aborting ...')

        except Exception as e:
            self.finish_log(f'The Tool {self.name} encountered the following error during execution: {e}. Aborting ...')

    def do(self):
        pass


    # ---------------------------------------------------
    # Logging

    def log(self, to_log : str) -> None:
        if not self.external_log is None:
            try:
                self.external_log(to_log)
            except Exception:
                print(f'[Error]: Failed to log tool message: {to_log}')

    def start_log(self, to_log) -> None:
        self.log(f'[Start]: {to_log}')

    def semantic_error(self,to_log):
        self.log(f'[Error]: {to_log}')

    def exception_log(self, to_log) -> None:
        to_log = f'[Error]: {to_log}'
        if not traceback.format_exc() is None:
            to_log +=f'Traceback: {traceback.format_exc()}'

        self.log(to_log)

    def progress_log(self, to_log) -> None:
        self.log(f'[Progress]: {to_log}')

    def finish_log(self, to_log) -> None:
        self.log(f'[Finish]: {to_log}')


class ToolInstruction:
    def __init__(self,name : str, arguments : dict):
        self.name : str = name
        self.arguments : dict = arguments

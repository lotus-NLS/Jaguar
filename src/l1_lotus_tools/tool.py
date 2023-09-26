import traceback
import json

from typing import Optional, Union, Callable, Any
from func_timeout import func_timeout, FunctionTimedOut
from src.l2_lotus_core import Agent
from src.l2_lotus_core import Tool as ToolInterface


# Generic tool class logging
# -> [START] : For tool launch
# -> [FINISH]: Tool done

# Specifc tool implementations (READ, WRITE etc.) logging:
# -> [Update] : For updates on tool progress
# -> [ERROR] : For reporting encountered errors if any

# ---------------------------------------------------------


verbose_mode_enabled = True

class ToolArg:
    def __init__(self, name: str, dtype : type, description: str,available_options : Optional[list[str]] = None,
                 is_required : bool = True):
        self.name : str = name
        self.dtype : type = dtype
        self.description : str = description
        self.val : dtype = None
        self.available_options: Optional[list[str]] = available_options
        self.is_required = is_required

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

    def value_is_valid(self) -> bool:
        if self.available_options is None:
            return True

        return self.val in self.available_options



class Tool(ToolInterface):
    timout_in_sec = 60

    def __init__(self):
        self.name : str = self.__class__.__name__
        self.desc : str = ''
        self.external_log : Callable = lambda *args, **kwargs: None
        self.arguments : list[ToolArg] = []
        self.is_enabled : bool = True
        self.acting_agent : Optional[Agent] = None

    def disable(self):
        self.is_enabled = False

    def create_arg(self, name: str, dtype: type, desc: str, available_options : Optional[list[str]] = None) -> ToolArg:
        this_arg = ToolArg(name, dtype, desc,available_options)
        self.arguments.append(this_arg)
        return this_arg

    # ---------------------------------------------------
    # Handle

    def get_json_doc(self) -> dict[str,Any]:
        tool_doc = {
            'name': f'{self.name}',
            'description': f'{self.desc}',
            'parameters': {
                'type': 'object',
                'properties': {}
            },
        }

        for arg in self.arguments:
            tool_doc['parameters']['properties'][arg.name] = arg.get_arg_json_doc()

        tool_doc['parameters']['required'] = [arg.name for arg in self.arguments if arg.is_required]

        if verbose_mode_enabled:
            print(f'Temp debug: {json.dumps(tool_doc,indent=4)}')

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
            if not arg.value_is_valid():
                self.finish_log(f'Call failed since value {arg.val} is not one of the available options {arg.available_options} for argument {arg.name}')
                return


        try:
            self.update_log(f'Tool {self.name} has been launched')
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

    def start_log(self, to_log : str) -> None:
        self.log(f'[Start]: {to_log}')

    def semantic_error(self,to_log: str):
        self.log(f'[Error]: {to_log}')

    def exception_log(self, to_log : str) -> None:
        to_log = f'[Error]: {to_log}'
        if not traceback.format_exc() is None:
            to_log += f'Traceback: {traceback.format_exc()}'

        self.log(to_log)

    def update_log(self, to_log: str) -> None:
        self.log(f'[Update]: {to_log}')

    def finish_log(self, to_log: str) -> None:
        self.log(f'[Finish]: {to_log}')

import traceback
import json
from typing import Any, Optional
from lotusEngine.pyutils import DevLogger
from func_timeout import func_timeout, FunctionTimedOut

from lotusEngine.l2_lotus_agent import Agent, ToolInterface, ToolArg

# Generic tool class logging
# -> [START] : For tool launch
# -> [FINISH]: Tool done

# Specifc tool implementations (READ, WRITE etc.) logging:
# -> [Update] : For updates on tool progress
# -> [ERROR] : For reporting encountered errors if any
# ---------------------------------------------------------

verbose_mode_enabled = False

class Tool(ToolInterface):
    timout_in_sec = 60

    @classmethod
    def make(cls, is_public_tool : bool = True):
        the_tool = cls()
        the_tool.is_public_tool = is_public_tool
        return the_tool

    def __init__(self, is_public_tool : bool = True):
        super().__init__()
        self.acting_agent: Optional[Agent] = None
        self.is_public_tool : bool = is_public_tool


    def create_arg(self, name: str, dtype: type, desc: str, available_options: Optional[list[str]] = None,
                   is_optional: bool = False) -> ToolArg:
        this_arg = ToolArg(name=name, dtype=dtype, desc=desc, available_options=available_options, is_optional=is_optional)
        self.arg_dict[this_arg.name] = this_arg

        return this_arg

    # ---------------------------------------------------
    # Handle

    def handle_call(self, args_dict: dict):
        self.reset_args()
        self.start_log(f'Attempting to launch tool {self.name} with args: {args_dict}')

        required_arguments_included = all([arg.name for arg in self._get_required_args_list()])
        if not required_arguments_included:
            self.finish_log(f'Call failed since provided dictionary {args_dict} did not cover all required tool arguments')
            return

        tool_args_specified = [arg for arg in self._get_arg_list() if arg.name in args_dict]
        for arg in tool_args_specified:
            arg.val = args_dict[arg.name]
            if not arg.value_is_valid():
                self.finish_log(
                    f'Call failed since value {arg.val} is not one of the available options {arg.available_options} for argument {arg.name}')
                return

        try:
            self.update_log(f'Tool {self.name} has been launched')
            func_timeout(timeout=Tool.timout_in_sec, func=self.do)
            self.finish_log(f'Tool {self.name} completed execution')

        except FunctionTimedOut:
            self.finish_log(
                f'The tool {self.name} timed out without completing after {Tool.timout_in_sec} seconds. Aborting ...')

        except Exception:
            self.finish_log(
                f'The Tool {self.name} encountered the following error during execution:\n{traceback.format_exc()}\n'
                f'Aborting ...')

    def do(self):
        pass
    # ---------------------------------------------------
    # Get

    def get_json_doc(self) -> dict[str, Any]:
        tool_doc = {
            'name': f'{self.name}',
            'description': f'{self.desc}',
            'parameters': {
                'type': 'object',
                'properties': {}
            },
        }

        for arg in self._get_arg_list():
            tool_doc['parameters']['properties'][arg.name] = arg.get_arg_json_doc()

        tool_doc['parameters']['required'] = [arg.name for arg in self._get_arg_list() if not arg.is_optional]

        if verbose_mode_enabled:
            print(f'Temp debug: {json.dumps(tool_doc, indent=4)}')

        if not self.get_is_json_serializable(tool_doc):
            raise ValueError(f'\n[Error]: Could not serialize object {tool_doc}\n'
                             f'Aborting ...')

        return tool_doc


    @staticmethod
    def get_is_json_serializable(json_obj: dict) -> bool:
        try:
            json.dumps(json_obj)
            return True
        except:
            return False


    def reset_args(self):
        for arg in self._get_arg_list():
            arg.val = None


    def _get_arg_list(self) -> list[ToolArg]:
        return list(self.arg_dict.values())


    def _get_required_args_list(self) -> list[ToolArg]:
        return [arg for arg in self._get_arg_list() if not arg.is_optional]


    # ---------------------------------------------------
    # Logging

    def _log(self, to_log: str):
        if not self.external_log is None:
            try:
                self.external_log(to_log)
            except Exception:
                print(f'[Error]: Failed to log tool message: {to_log}')


    def start_log(self, to_log: str):
        self._log(f'[Start]: {to_log}')


    def semantic_error(self, to_log: str):
        self._log(f'[Error]: {to_log}')


    def exception_log(self, to_log: str):
        self._log(DevLogger.get_exception_msg(to_log))


    def update_log(self, to_log: str):
        self._log(f'[Update]: {to_log}')


    def finish_log(self, to_log: str):
        self._log(f'[Finish]: {to_log}')



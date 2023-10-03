from typing import Union, Optional
import json

# 08.09.23: (D.H.):
# The agent has two options for an action: "Speak" or "Use a tool"
# The content of an action is either the text which is to be spoken or the instructions for the tool usage

# ---------------------------------------------------------

class ToolAction:
    def __init__(self,name : str, arguments : dict):
        self._name : str = name
        self._arguments : dict = arguments

    def get_tool_name(self) -> str:
        return self._name

    def get_arguments_(self) -> dict:
        return self._arguments


class ActionOptions:
    def __init__(self, is_allowed_functioncall : bool, max_tokens : Optional[int], temperature : float = 0.3):
        self.is_allowed_functioncall = is_allowed_functioncall
        self.max_tokens = max_tokens
        self.temperature = temperature


class Action:
    def __init__(self, openAI_response : dict):
        try:
            self._best_response : dict = openAI_response['choices'][0]['message']
        except:
            print('[Debug]: Failed to retrieve response from OpenAI. Defaulting to empty action')
            self._best_response  : dict = {}

    # To my knowledge 'content' is always a key in the dict but not always filled with IdentityDefinitions
    def get_text(self) -> Union[str, None]:
        content = self._best_response['content'] if 'content' in self._best_response else None
        return content if isinstance(content,str) else None


    def get_tool_action(self) -> Union[ToolAction, None]:
        funct_call = self._best_response['function_call'] if 'function_call' in self._best_response else None

        if funct_call is None:
            return

        if not isinstance(funct_call, dict):
            print(f'[Debug]: Provided funct_call {funct_call} is not of dict type')
            return

        if not 'name' in funct_call:
            print(f'[Debug]: Could not find name in dictionary. Aborting ... ')
            return

        if not 'arguments' in funct_call:
            print(f'[Debug: Could not find arguments in dictionary. Aborting ...')
            return

        try:
            tool_name = funct_call['name']
            if not isinstance(tool_name, str):
                raise TypeError

            json_str = funct_call['arguments']

            try:
                tool_args_dict = json.loads(s=json_str)
            except:
                print(f'[Debug]: Given json string {json_str} is invalid. Attempting to salvage ...')
                tool_args_dict = json.loads(s=self.get_salvaged_json(broken_json=json_str))

        except:
            print(f'[Debug]: An error occured while trying to parse given function call {funct_call}. Raising exception ...')
            raise ValueError('Unable to parse tool instructions ')

        return ToolAction(name=tool_name, arguments=tool_args_dict)


    @staticmethod
    def get_salvaged_json(broken_json: str) -> str:
        currently_inside_quotes = False
        next_char_escaped = False
        escaped = []

        control_char_map = {
            '\n': '\\n',
            '\t': '\\t',
            '\r': '\\r',
            '\b': '\\b',
            '\f': '\\f',
            '\\': '\\\\'
        }

        for char in broken_json:
            if char == '"' and not next_char_escaped:
                currently_inside_quotes = not currently_inside_quotes

            if currently_inside_quotes and not next_char_escaped:
                if char in control_char_map:
                    escaped.append(control_char_map[char])
                    continue

            if char == '\\':
                next_char_escaped = True
            else:
                next_char_escaped = False

            escaped.append(char)

        return ''.join(escaped)


    def __str__(self):
        return str(self._best_response)

from typing import Union, Optional
import json
from src.l2_lotus_core.m0_agent.tool import ToolInstruction

# 08.09.23: D.H.:
# The agent has two options for an action: "Speak" or "Use a tool"
# The content of an action is either the text which is to be spoken or the instructions for the tool usage

# ---------------------------------------------------------


class ActionContent:
    def __init__(self, openAI_response : dict):
        try:
            self._best_response : dict = openAI_response['choices'][0]['message']
        except:
            print('[Debug]: Failed to retrieve response from OpenAI. Defaulting to empty action')
            self._best_response  : dict = {}

    # To my knowledge 'content' is always a key in the dict but not always filled with IdentityDefinitions
    def get_text_content(self) -> Union[str,None]:
        content = self._best_response['content'] if 'content' in self._best_response else None
        return content if isinstance(content,str) else None


    def get_tool_instructions(self) -> Union[ToolInstruction, None]:
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
            tool_args_dict = json.loads(funct_call['arguments'])

            if not isinstance(tool_name,str):
                raise TypeError
            if not isinstance(tool_args_dict,dict):
                raise TypeError
        except:
            print(f'[Debug]: An error occured while trying to parse given tool arguments. Aborting ...')
            return


        return ToolInstruction(name=tool_name, arguments=tool_args_dict)


class ActionOptions:
    def __init__(self, is_allowed_functioncall : bool, max_tokens : Optional[int], temperature : float = 0.3):
        self.is_allowed_functioncall = is_allowed_functioncall
        self.max_tokens = max_tokens
        self.temperature = temperature

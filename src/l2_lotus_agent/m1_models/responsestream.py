from __future__ import annotations
from pyutils import get_salvaged_json
from typing import Optional
import json


# ---------------------------------------------------------

class ToolCall:
    def __init__(self):
        self.name : Optional[str]  = None
        self.json_str : Optional[str] = None
        self._arguments : Optional[dict] = None

    def update(self, partial_tool_call : Optional[ToolCall]):
        if partial_tool_call is None:
            return
        if self.json_str is None:
            self.json_str = ''

        other_name = partial_tool_call.name
        other_jstr = partial_tool_call.json_str

        if not other_name is None:
            self.name = other_name
        if not other_jstr is None:
            self.json_str += other_jstr

    def get_tool_name(self) -> str:
        return self.name

    def get_arguments(self) -> dict:
        return self._arguments

    def parse_json(self):
        json_str = self.json_str

        try:
            tool_args_dict = json.loads(s=json_str)
        except:
            print(f'[Debug]: Given json string {json_str} is invalid. Attempting to salvage ...')
            tool_args_dict = json.loads(s=get_salvaged_json(broken_json=json_str))

        self._arguments = tool_args_dict



class Chunk:
    def __init__(self, data):
        self.data = data
        self.best_response : Optional[dict]  = self.data['choices'][0].get('delta')

    def get_text_chunk(self) -> Optional[str]:
        text_content = None
        if not self.best_response is None:
            text_content = self.best_response.get('content')
        return text_content


    # To my knowledge 'content' is always a key in the dict but not always filled with IdentityDefinitions
    def get_function_chunk(self) -> Optional[ToolCall]:
        funct_call : dict = self.best_response.get('function_call')

        if funct_call is None:
            return None

        partial_call = ToolCall()
        partial_call.json_str = funct_call.get('arguments')
        partial_call.name = funct_call.get('name')

        return partial_call

# TODO: Can aggregate the content in the container by overriding __next__
# TODO: Could also do implement a convert to string method to eleiminate get_text_response from agent
class ResponseStream(dict):
    def __new__(cls, openAI_response : dict):
        return openAI_response



class FunctCallOption:

    @classmethod
    def make_no_call_option(cls):
        return cls(call_allowed=False)

    @classmethod
    def make_auto_option(cls):
        return cls(call_allowed=True)

    def __init__(self, call_allowed : bool = True, required_funct_name : Optional[str] = None):
        self.call_allowed : bool = call_allowed
        self.required_funct_name : Optional[str] = required_funct_name

    def get_openai_syntax(self) -> object:
        if not self.call_allowed:
            return 'none'

        if self.required_funct_name is None:
            return 'auto'
        else:
            return {'name' : f'{self.required_funct_name}'}


class ActionOptions:
    def __init__(self, funct_call_options : FunctCallOption, max_tokens : Optional[int] = None, temperature : float = 0.3):
        self.funct_call_options : FunctCallOption = funct_call_options
        self.max_tokens : int = max_tokens
        self.temperature : float = temperature


    def get_funct_call_allowed(self):
        return self.funct_call_options.call_allowed

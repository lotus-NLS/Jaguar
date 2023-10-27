from __future__ import annotations
from engine.pyutils import get_salvaged_json
from typing import Optional, Generator, Iterator
import json
from openai.openai_object import OpenAIObject
# ---------------------------------------------------------

class ActionStream:

    @classmethod
    def make_empty(cls) -> ActionStream:
        return cls(openai_generator=None)

    def __init__(self, openai_generator : Optional[Generator]):
        self.generator_data : Optional[Generator] = openai_generator
        self.text_content : str = ''

    def __iter__(self) -> Iterator[ActionChunk]:
        return self


    def exhaust(self):
        for chunk in self:
            _ = chunk

    def __next__(self) -> ActionChunk:
        if self.generator_data is None:
            raise StopIteration

        action_chunk = ActionChunk(data=self.generator_data.__next__())
        chunk_text = action_chunk.get_text_chunk()
        self.text_content += chunk_text if not chunk_text is None else ''
        return action_chunk


class ActionChunk:

    def __init__(self, data : OpenAIObject):
        self.response_data : OpenAIObject = data
        self.best_response : Optional[dict]  = self.response_data['choices'][0].get('delta')


    def get_text_chunk(self) -> Optional[str]:
        text_content = None
        if not self.best_response is None:
            text_content = self.best_response.get('content')
        return text_content


    def get_function_chunk(self) -> Optional[ToolCall]:
        funct_call : Optional[dict] = self.best_response.get('function_call')

        if funct_call is None:
            tool_call = None
        else:
            tool_call = ToolCall(name=funct_call.get('name'), json_str=funct_call.get('arguments'))

        return tool_call


class ToolCall:
    @classmethod
    def make_empty(cls):
        return cls(name=None, json_str=None)

    def __init__(self, name : Optional[str], json_str : Optional[str]):
        self.name : str  = name if not name is None else ''
        self.json_str : str = json_str if not json_str is None else ''
        self._arguments : Optional[dict] = None
        self.is_empty = True


    def update(self, partial_tool_call : ToolCall):
        self.is_empty = False
        self.name += partial_tool_call.name
        self.json_str += partial_tool_call.json_str


    def try_parse_json(self):
        json_str = self.json_str

        try:
            tool_args_dict = json.loads(s=json_str)
        except:
            print(f'[Debug]: Given json string {json_str} is invalid. Attempting to salvage ...')
            tool_args_dict = json.loads(s=get_salvaged_json(broken_json=json_str))

        self._arguments = tool_args_dict

    # ---------------------------------------------------
    # Actions

    def get_tool_name(self) -> str:
        return self.name

    def get_arguments(self) -> dict:
        return self._arguments








from __future__ import annotations

import logging
from json_repair import repair_json
from typing import Optional, Generator, Iterator
import json
from openai.openai_object import OpenAIObject
from typing import Union
# ---------------------------------------------------------

class Generation:
    @classmethod
    def make_empty(cls) -> Generation:
        return cls(generator=None)

    def __init__(self, generator : Optional[Generator]):
        self.generator : Optional[Generator] = generator
        self.text_content : str = ''

    def __iter__(self) -> Iterator[Chunk]:
        return self


    def __next__(self) -> Chunk:
        if self.generator is None:
            raise StopIteration

        action_chunk = Chunk(data=self.generator.__next__())
        chunk_text = action_chunk.get_text()
        self.text_content += chunk_text if not chunk_text is None else ''
        return action_chunk


class Chunk:
    def __init__(self, data : OpenAIObject):
        self.response_data : OpenAIObject = data
        self.best_response : Optional[dict]  = self.response_data['choices'][0].get('delta')


    def get_text(self) -> Optional[str]:
        text_content = None
        if not self.best_response is None:
            text_content = self.best_response.get('content')
        return text_content


    def get_call(self) -> Optional[MultiToolCall]:
        tool_calls : Optional[dict] = self.best_response.get('tool_calls')
        if tool_calls is None:
            return None

        multitool_call = MultiToolCall()
        for openai_tool_call in tool_calls:
            index = openai_tool_call.get('index')
            funct_call = openai_tool_call.get('function')

            tool_call = SingleToolCall(name=funct_call.get('name'), json_str=funct_call.get('arguments'), index=index)
            multitool_call.update(tool_call=tool_call)

        return multitool_call


class MultiToolCall:
    def __init__(self):
        self.tool_calls : dict[int,SingleToolCall] = {}


    def update(self, tool_call : Union[SingleToolCall, MultiToolCall]):
        if isinstance(tool_call, SingleToolCall):
            index = tool_call.index
            if self.tool_calls.get(index) is None:
                self.tool_calls[index] = tool_call
            else:
                self.tool_calls[index].update(partial_tool_call=tool_call)
        elif isinstance(tool_call, MultiToolCall):
            for tool_call in tool_call.get_as_list():
                self.update(tool_call=tool_call)

    def get_as_list(self):
        return self.tool_calls.values()



class SingleToolCall:
    def __init__(self, name : Optional[str], json_str : Optional[str], index : int):
        self.index : int  = index
        self.name : str  = name if not name is None else ''
        self.json_str : str = json_str if not json_str is None else ''
        self._arguments : Optional[dict] = None
        self.is_empty = True


    def update(self, partial_tool_call : SingleToolCall):
        self.is_empty = False
        self.name += partial_tool_call.name
        self.json_str += partial_tool_call.json_str



    def try_parse_json(self):
        json_str = self.json_str

        try:
            tool_args_dict = json.loads(s=json_str)
        except:
            logging.error(f'Given json string {json_str} is invalid. Attempting to salvage ...')
            tool_args_dict = json.loads(s=repair_json(json_str=json_str))

        self._arguments = tool_args_dict

    # ---------------------------------------------------
    # Actions

    def __str__(self):
        try:
            the_str = str(self.json_str)
        except:
            the_str = ''
        return the_str

    def get_tool_name(self) -> str:
        return self.name

    def get_arguments(self) -> dict:
        return self._arguments



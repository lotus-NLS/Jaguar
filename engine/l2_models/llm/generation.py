from __future__ import annotations

from typing import Optional, Generator, Iterator
from openai.openai_object import OpenAIObject

from engine.l2_models import SingleToolCall, MultiToolCall
from engine.l3_toolbox import Tool

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


class GenerationOptions:
    def __init__(self, funct_call_options : ToolOptions, max_tokens : Optional[int] = None, temperature : float = 0.3):
        self.tool_options : ToolOptions = funct_call_options
        self.max_tokens : int = max_tokens
        self.temperature : float = temperature

    def get_funct_call_allowed(self):
        return self.tool_options.call_allowed


class ToolOptions:
    @classmethod
    def no_call(cls):
        return cls(allowed=False)

    @classmethod
    def auto(cls):
        return cls(allowed=True)


    def __init__(self, allowed : bool = True, required_tool : Optional[Tool] = None):
        self.call_allowed : bool = allowed
        self.required_tool : Optional[str] = required_tool

        if not self.call_allowed and self.required_tool:
            raise ValueError('Cannot require a tool call if the call is not allowed')


    def get_openai_syntax(self) -> object:
        if not self.call_allowed:
            return 'none'

        if self.required_tool is None:
            return 'auto'
        else:
            return {"type" : "function", "function" : {'name' : f'{self.required_tool}'}}

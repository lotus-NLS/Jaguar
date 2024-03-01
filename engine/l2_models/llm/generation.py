from __future__ import annotations

from typing import Optional, Generator, Iterator
from dataclasses import dataclass
from abc import abstractmethod

from api import Entry
from engine.l3_applications.tool import ToolCall
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

        action_chunk = self.get_next_chunk(data=self.generator.__next__())
        chunk_text = action_chunk.get_text()
        self.text_content += chunk_text if not chunk_text is None else ''
        return action_chunk

    @abstractmethod
    def get_next_chunk(self, data : object):
        pass



class Chunk:
    def __init__(self, data : object):
        self.data = data

    @abstractmethod
    def get_text(self) -> Optional[str]:
        pass


    @abstractmethod
    def get_call(self) -> Optional[ToolCall]:
        pass


@dataclass
class GenerationContext:
    entries : list[Entry]
    docs : list[dict]


@dataclass
class ToolOptions:
    call_allowed: bool
    required_tool: Optional[str] = None

    @classmethod
    def no_call(cls):
        return cls(call_allowed=False)

    @classmethod
    def auto(cls):
        return cls(call_allowed=True)


    def __post_init__(self):
        if not self.call_allowed and self.required_tool:
            raise ValueError('Cannot require a tool call if the call is not allowed')


    def get_openai_syntax(self) -> object:
        if not self.call_allowed:
            return 'none'

        if self.required_tool is None:
            return 'auto'
        else:
            return {"type" : "function", "function" : {'name' : f'{self.required_tool}'}}


@dataclass
class Options:
    tool_options : ToolOptions = ToolOptions.auto()
    max_tokens : Optional[int] = None
    temp : float = 0.3

    def get_call_allowed(self):
        return self.tool_options.call_allowed

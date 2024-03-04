from __future__ import annotations

from typing import Optional, Generator, Iterator
from dataclasses import dataclass
from abc import abstractmethod
from queue import Queue
from api import Entry
from hollarek.logging import Loggable, LogLevel, LogSettings
from engine.l4_tools import CallMap
from engine.l5_singletons.io import Task

# ---------------------------------------------------------

class Generation(Loggable):
    stop_token = '⊥'

    def __init__(self, generator : Generator):
        super().__init__(settings=LogSettings(include_call_location=True))
        self.generator : Generator = generator
        self.text_content : str = ''
        self.text_queue : Queue[str] = Queue()

    def __iter__(self) -> Iterator[Chunk]:
        return self


    def __next__(self) -> Chunk:
        chunk = self._get_next_chunk(chunk_data=self.generator.__next__())
        chunk_text = chunk.get_text()
        if chunk_text:
            self.text_queue.put(chunk_text)
        if chunk.is_final():
            self.stop()
        self.text_content += chunk_text if not chunk_text is None else ''
        return chunk


    @abstractmethod
    def _get_next_chunk(self, chunk_data : object):
        pass

    def stop(self):
        self.text_queue.put(self.stop_token)

    async def get_text_stream(self):
        while True:
            try:
                retrieved_text = self.text_queue.get(timeout=10)
            except:
                self.log('No text retrieved', level=LogLevel.ERROR)
                break
            if retrieved_text == Generation.stop_token:
                break
            yield retrieved_text


class Chunk:
    def __init__(self, data : object):
        self.data = data

    @abstractmethod
    def get_text(self) -> Optional[str]:
        pass


    @abstractmethod
    def is_final(self) -> bool:
        pass

    @abstractmethod
    def get_call_map(self) -> CallMap:
        pass


@dataclass
class GenerationContext:
    entries : list[Entry]
    docs : list[dict]


@dataclass
class ToolOptions:
    call_allowed: bool
    required_tool_name: Optional[str] = None

    @classmethod
    def no_call(cls):
        return cls(call_allowed=False)

    @classmethod
    def auto(cls):
        return cls(call_allowed=True)


    def __post_init__(self):
        if not self.call_allowed and self.required_tool_name:
            raise ValueError('Cannot require a tool call if the call is not allowed')


    def get_openai_syntax(self) -> object:
        if not self.call_allowed:
            return 'none'

        if self.required_tool_name is None:
            return 'auto'
        else:
            return {"type" : "function", "function" : {'name' : f'{self.required_tool_name}'}}


@dataclass
class Options:
    tool_options : ToolOptions = ToolOptions.auto()
    max_tokens : Optional[int] = None
    temp : float = 0.3

    @classmethod
    def from_task(cls, task : Task):
        return cls(tool_options=ToolOptions(call_allowed=True, required_tool_name=task.required_tool_name))

    def get_call_allowed(self):
        return self.tool_options.call_allowed

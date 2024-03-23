from __future__ import annotations

from typing import Optional, Iterator
from dataclasses import dataclass, field
from abc import abstractmethod
from api import Entry
from hollarek.core.logging import Loggable, LogSettings
from engine.l4_tools import CallMap, ToolDoc

# ---------------------------------------------------------

class Generation(Loggable):
    stop_token = '⊥'

    def __init__(self, generator : Iterator, chunk_type : type[Chunk]):
        super().__init__(settings=LogSettings(include_call_location=True))
        self.generator : Iterator = generator
        self.chunk_type : type[Chunk] = chunk_type
        self.text_content : str = ''
        self.call_map = CallMap()
        self.is_done : bool = False

    def _get_next_chunk(self, chunk_data : object):
        return self.chunk_type(data=chunk_data)

    def exhaust(self):
        for _ in self:
            pass

    def __iter__(self) -> Iterator[Chunk]:
        return self

    def __next__(self) -> Chunk:
        chunk = self._get_next_chunk(chunk_data=self.generator.__next__())
        self.add_text(chunk)
        self.add_calls(chunk)

        if chunk.is_final():
            self.stop()

        return chunk

    def add_text(self, chunk: Chunk):
        text = chunk.get_text()
        if not text is None:
            self.text_content += text

    def add_calls(self, chunk : Chunk):
        chunk_call_map = chunk.get_call_map()
        self.call_map.add(chunk_call_map)


    def stop(self):
        self.is_done = True

    # ---------------------------------------------------------
    # get

    def get_call_map(self):
        if not self.is_done:
            raise ValueError('Generation is not done yet')
        return self.call_map

    def get_text(self) -> str:
        if not self.is_done:
            raise ValueError('Generation is not done yet')
        return self.text_content



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
class Context:
    entries: list[Entry] = field(default_factory=list)
    docs: list[ToolDoc] = field(default_factory=list)

    def add_entry(self, entry : Entry):
        self.entries.append(entry)

    def reset(self):
        self.entries = []

    def __iadd__(self, other : Context):
        if not isinstance(other,Context):
            raise TypeError(f'Cannot add Context with {type(other)}')
        return Context(entries=self.entries + other.entries, docs=self.docs + other.docs)

    def as_str(self, section_header : str) -> str:
        def get_seperator(name : str) -> str:
            max_len = 100
            num_dashes = max(0, max_len-len(name))
            dashes = '-'*int(num_dashes/2.)
            return '\n+' + dashes + f' {name} '+ dashes + '+\n'

        context_str = get_seperator(name=section_header)
        for entry in self.entries:
            context_str += f'{entry.as_str()}\n'

        for doc in self.docs:
            context_str += f'{doc.as_str(pretty=True)}\n'
        return context_str

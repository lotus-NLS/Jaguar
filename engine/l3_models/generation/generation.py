from __future__ import annotations

from typing import Optional, Iterator
from dataclasses import dataclass, field
from abc import abstractmethod
from queue import Queue
from api import Entry
from hollarek.logging import Loggable, LogLevel, LogSettings
from engine.l4_tools import CallMap

# ---------------------------------------------------------

class Generation(Loggable):
    stop_token = '⊥'

    def __init__(self, generator : Iterator):
        super().__init__(settings=LogSettings(call_location=True))
        self.generator : Iterator = generator
        self.text_content : str = ''
        self.call_map = CallMap()
        self.is_done : bool = False

    @abstractmethod
    def _get_next_chunk(self, chunk_data : object):
        pass

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
    docs: list[dict] = field(default_factory=list)

    def add_entry(self, entry : Entry):
        self.entries.append(entry)

    def reset(self):
        self.entries = []

    def __iadd__(self, other):
        return Context(entries=self.entries + other.entries, docs=self.docs + other.docs)
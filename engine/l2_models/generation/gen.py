from __future__ import annotations

# import sys
# import time
from typing import Optional, Iterator
from abc import abstractmethod

from engine.l3_aos.tools import ToolCall

# ---------------------------------------------------------

class Generation:
    def __init__(self, generator : Iterator, chunk_type : type[Chunk]):
        self.generator : Iterator = generator
        self.chunk_type : type[Chunk] = chunk_type

        self.is_done : bool = False
        self.text : str = ''
        self.toolcall_map : dict[int, ToolCall] = {}

    def exhaust(self):
        for _ in self:
            pass

    def __iter__(self) -> Iterator[Chunk]:
        return self

    def __next__(self) -> Chunk:
        chunk = self.chunk_type(data=self.generator.__next__())
        self._add_text(chunk)
        self._add_toolcalls(chunk)

        if chunk.is_final():
            self._stop()

        return chunk

    def _add_text(self, chunk: Chunk):
        text = chunk.get_text()
        if not text is None:
            # time.sleep(0.05)
            # print(text, end='')
            # sys.stdout.flush()
            self.text += text

    def _add_toolcalls(self, chunk : Chunk):
        toolcall_map : dict[int, ToolCall] = chunk.get_call_map()
        for idx, tool_call in toolcall_map.items():

            if not idx in self.toolcall_map:
                self.toolcall_map[idx] = tool_call
            else:
                self.toolcall_map[idx].update(tool_call)

    def _stop(self):
        self.is_done = True

    # ---------------------------------------------------------
    # get

    def get_tool_calls(self) -> list[ToolCall]:
        if not self.is_done:
            raise ValueError('Generation is not done yet')
        return list(self.toolcall_map.values())

    def get_text(self) -> str:
        if not self.is_done:
            raise ValueError('Generation is not done yet')
        return self.text



class Chunk:
    def __init__(self, data : object):
        self.data = data

    @abstractmethod
    def get_text(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_call_map(self) -> dict[int, ToolCall]:
        pass

    @abstractmethod
    def is_final(self) -> bool:
        pass



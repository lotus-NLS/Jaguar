from __future__ import annotations

from typing import Optional, Iterator
from abc import abstractmethod

from engine.l3_aos.tools import ToolCall

# ---------------------------------------------------------

class Generation:
    def __init__(self, generator : Iterator, chunk_type : type[Chunk]):
        self.generator : Iterator = generator
        self.chunk_type : type[Chunk] = chunk_type

        self.is_done : bool = False
        self.text_content : str = ''
        self.tool_call_map : dict[int, ToolCall] = {}

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
            self.text_content += text

    def _add_toolcalls(self, chunk : Chunk):
        toolcall_map : dict[int, ToolCall] = chunk.get_call_map()
        for idx, tool_call in toolcall_map.items():
            print(f'idx, toolcall = {idx} {tool_call}')
            if not idx in self.tool_call_map:
                self.tool_call_map[idx] = tool_call
            else:
                self.tool_call_map[idx].update(tool_call)

    def _stop(self):
        self.is_done = True

    # ---------------------------------------------------------
    # get

    def get_tool_calls(self) -> list[ToolCall]:
        if not self.is_done:
            raise ValueError('Generation is not done yet')
        return list(self.tool_call_map.values())

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
    def get_call_map(self) -> dict[int, ToolCall]:
        pass

    @abstractmethod
    def is_final(self) -> bool:
        pass



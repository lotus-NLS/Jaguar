from __future__ import annotations

from typing import Optional, Iterator
from dataclasses import dataclass, field
from abc import abstractmethod

from func_timeout import func_timeout, FunctionTimedOut

from api import Entry
from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolDoc, ToolCall

# ---------------------------------------------------------

class Generation:
    def __init__(self, generator : Iterator, chunk_type : type[Chunk]):
        self.generator : Iterator = generator
        self.chunk_type : type[Chunk] = chunk_type

        self.is_done : bool = False
        self.text_content : str = ''
        self.tool_calls : dict[int, ToolCall] = {}

    def __iter__(self) -> Iterator[Chunk]:
        return self

    def __next__(self) -> Chunk:
        chunk = self.chunk_type(data=self.generator.__next__())
        self.add_text(chunk)
        self.add_args(chunk)

        if chunk.is_final():
            self.stop()

        print(f'Processsing chunk')
        print(f'Tool call zero json str = {list(self.tool_calls.values())[0].json_str}')

        return chunk

    def add_text(self, chunk: Chunk):
        text = chunk.get_text()
        if not text is None:
            self.text_content += text

    def add_args(self, chunk : Chunk):
        callmap : dict[int, ToolCall] = chunk.get_call_map()
        print(f'Callmap = {callmap}')
        for name, tool_call in callmap.items():
            if not name in self.tool_calls:
                self.tool_calls[name] = tool_call
            else:
                self.tool_calls[name].add(tool_call)

    def stop(self):
        self.is_done = True

    # ---------------------------------------------------------
    # get

    def get_tool_calls(self) -> list[ToolCall]:
        if not self.is_done:
            raise ValueError('Generation is not done yet')
        return list(self.tool_calls.values())

    def get_text(self) -> str:
        if not self.is_done:
            raise ValueError('Generation is not done yet')
        return self.text_content

    def print_action_info(self):
        print(f'\n-> Generated tool calls')
        for call in self.get_tool_calls():
            print(f'tool name: {call.name}')
            print(call.get_args_dict())

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
    def get_call_map(self) -> dict[int, ToolCall]:
        pass


@dataclass
class Context:
    entries: list[Entry] = field(default_factory=list)
    docs: list[ToolDoc] = field(default_factory=list)

    @classmethod
    def from_aos(cls, aos : AOS):
        open_workspaces = [workspace for workspace in aos.get_workspaces() if workspace.is_active]
        entries = []
        for workspace in open_workspaces:
            try:
                entry = func_timeout(func=workspace.get_entry, timeout=10)
                entries.append(entry)
            except FunctionTimedOut:
                aos.error(f'Workspace get entry out timed for workspace \"{workspace.get_name()}\"')
            except BaseException as e:
                aos.error(f'Error in getting entry for app \"{workspace.get_name()}\": {e}')
        docs = aos.get_action_docs()
        return cls(entries=entries, docs=docs)

    def add_entry(self, entry : Entry):
        self.entries.append(entry)

    def reset(self):
        self.entries = []

    def __iadd__(self, other : Context):
        return Context(entries=self.entries + other.entries, docs=self.docs + other.docs)

    def as_str(self, section_header : str) -> str:
        def big_seperator(name : str) -> str:
            max_len = 100
            num_dashes = max(0, max_len-len(name))
            dashes = '-'*int(num_dashes/2.)
            return '\n+' + dashes + f' {name} '+ dashes + '+\n'

        def small_seperator(name : str) -> str:
            return f'----->> {name}\n'


        context_str = big_seperator(name=section_header)
        context_str += small_seperator(f'Workspace context') if self.docs else ''
        for entry in self.entries:
            context_str += f'{entry.as_str()}\n'

        context_str += small_seperator(f'Tool docs') if self.docs else ''
        context_str += '\n'
        for doc in self.docs:
            context_str += f'{doc.as_str()}\n\n'
        return context_str



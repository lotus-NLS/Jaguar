from __future__ import annotations

from dataclasses import dataclass, field

from func_timeout import func_timeout, FunctionTimedOut

from api import Entry
from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolDoc


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

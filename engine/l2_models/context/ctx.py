from __future__ import annotations

from dataclasses import dataclass, field

from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolDoc
from .entry import Entry


# -------------------------------------------------

@dataclass
class Context:
    entries: list[Entry] = field(default_factory=list)
    docs: list[ToolDoc] = field(default_factory=list)

    @classmethod
    def singleton(cls, entry : Entry) -> Context:
        return cls(entries=[entry])

    @classmethod
    def from_aos(cls, aos : AOS):
        open_workspaces = [workspace for workspace in aos.get_workspaces() if workspace.is_active]
        entries = []
        for workspace in open_workspaces:
            try:
                entry = Entry.from_workspace(workspace=workspace)
                entries.append(entry)
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

    def __add__(self, other : Context):
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
        context_str += small_seperator(f'Tool docs') if self.docs else ''
        context_str += '\n'
        for doc in self.docs:
            context_str += f'{doc.as_str()}\n\n'

        context_str += small_seperator(f'Memory')
        for entry in self.entries:
            context_str += f'{entry.as_str()}\n'

        return context_str

    def __eq__(self, other : Context):
        entry_lens_eq = len(self.entries) == len(other.entries)
        entries_equal = all([e1 == e2 for e1,e2 in zip(self.entries, other.entries)])

        doc_lens_eq = len(self.docs) == len(other.docs)
        docs_equal = all([d1 == d2 for d1,d2 in zip(self.docs, other.docs)])

        return entry_lens_eq and entries_equal and doc_lens_eq and docs_equal
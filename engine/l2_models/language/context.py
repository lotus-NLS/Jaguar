from __future__ import annotations

import json
from dataclasses import dataclass, field

from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolDoc
from holytools.abstract import JsonDataclass
from holytools.logging import LoggerFactory
from .entry import Entry

logger = LoggerFactory.get_logger(name=__name__)

# -------------------------------------------------

@dataclass
class Context(JsonDataclass):
    entries: list[Entry] = field(default_factory=list)
    docs: list[ToolDoc] = field(default_factory=list)

    @staticmethod
    def get_basic_entry(obj):
        if isinstance(obj, ToolDoc):
            return json.dumps(obj)
        return JsonDataclass.get_basic_entry(obj)

    @staticmethod
    def make_basic(basic_cls, s : str):
        if basic_cls == ToolDoc:
            the_dict = json.loads(s)
            return ToolDoc(the_dict)
        return JsonDataclass.make_basic(basic_cls, s)

    @classmethod
    def singleton(cls, entry : Entry) -> Context:
        return cls(entries=[entry])

    @classmethod
    def from_aos(cls, aos : AOS):
        entries = []
        for ws in [workspace for workspace in aos.workspaces if workspace.is_active]:
            try:
                entry = Entry.from_workspace(ws=ws)
                entries.append(entry)
            except BaseException as e:
                logger.error(f'Error in getting entry for app \"{ws.get_name()}\": {e}')

        tools = aos.get_tools()
        docs = [tool.get_doc() for tool in tools]

        return cls(entries=entries, docs=docs)

    @classmethod
    def get_example_context(cls, msg : str = 'I am GOTO') -> Context:
        entries : list[Entry] = [Entry.system(msg=msg), Entry.user(msg=f'Hello there')]
        basic_context = Context(entries=entries)

        aos = AOS.terminal_only()
        aos_context = Context.from_aos(aos=aos)
        return aos_context + basic_context

    # ---------------------------------------------------

    def get_view(self, section_header : str) -> str:
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
            context_str += f'{doc.get_view()}\n\n'

        context_str += small_seperator(f'Memory')
        for entry in self.entries:
            context_str += f'{entry.get_view()}\n'

        return context_str

    def __iadd__(self, other : Context):
        return Context(entries=self.entries + other.entries, docs=self.docs + other.docs)

    def __add__(self, other : Context):
        return Context(entries=self.entries + other.entries, docs=self.docs + other.docs)

    def __eq__(self, other : Context):
        entry_lens_eq = len(self.entries) == len(other.entries)
        entries_equal = all([e1 == e2 for e1,e2 in zip(self.entries, other.entries)])

        doc_lens_eq = len(self.docs) == len(other.docs)
        docs_equal = all([d1 == d2 for d1,d2 in zip(self.docs, other.docs)])

        return entry_lens_eq and entries_equal and doc_lens_eq and docs_equal
from __future__ import annotations

import json
import traceback
from dataclasses import dataclass, field

from engine.l3_aos.tools import ToolDoc
from holytools.abstract import JsonDataclass
from holytools.logging import LoggerFactory
from .message import Message, Role
from engine.l3_aos.aos import AOS

logger = LoggerFactory.get_logger(name=__name__)

# -------------------------------------------------

@dataclass
class Context(JsonDataclass):
    messages: list[Message] = field(default_factory=list)
    docs: list[ToolDoc] = field(default_factory=list)

    def interweave_workspaces(self, aos : AOS):
        msg_map = self.get_entry_map(aos=aos)
        for j, m in enumerate(reversed(self.messages)):
            matching_ws_name = self.get_matching_ws_name(ws_names=list(msg_map.keys()), tool_name=m.text)
            if m.role == Role.TOOL and not matching_ws_name is None:
                index, msg = len(self.messages)-j, msg_map[matching_ws_name]
                self.messages.insert(index, msg)
                del msg_map[matching_ws_name]

    @staticmethod
    def get_matching_ws_name(ws_names: list[str], tool_name: str):
        for n in ws_names:
            if n in tool_name:
                return n

    @staticmethod
    def get_entry_map(aos : AOS) -> dict[str, Message]:
        msg_map: dict[str, Message] = {}
        for ws in [workspace for workspace in aos.workspaces if workspace.is_open]:
            try:
                msg_map[ws.get_name()] = Message.from_workspace(ws=ws)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(f'Error in getting entry for app "{ws.get_name()}": {e}\nTraceback: {tb}')
        return msg_map


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
    def singleton(cls, entry : Message) -> Context:
        return cls(messages=[entry])

    @classmethod
    def get_example_context(cls, msg : str = 'I am GOTO') -> Context:
        entries : list[Message] = [Message.system(msg=msg), Message.user(msg=f'Hello there')]
        basic_context = Context(messages=entries)
        return basic_context

    # ---------------------------------------------------

    def get_view(self) -> str:
        def big_seperator(name : str) -> str:
            max_len = 100
            num_dashes = max(0, max_len-len(name))
            dashes = '-'*int(num_dashes/2.)
            return '\n+' + dashes + f' {name} '+ dashes + '+\n'

        context_str = ''
        context_str += big_seperator(f'Tool docs') if self.docs else ''
        context_str += '\n'
        for doc in self.docs:
            context_str += f'{doc.get_view()}\n\n'

        context_str += big_seperator(f'Memory')
        for entry in self.messages:
            context_str += f'{entry.get_view()}\n'

        return context_str

    def __iadd__(self, other : Context):
        return Context(messages=self.messages + other.messages, docs=self.docs + other.docs)

    def __add__(self, other : Context):
        return Context(messages=self.messages + other.messages, docs=self.docs + other.docs)

    def __eq__(self, other : Context):
        entry_lens_eq = len(self.messages) == len(other.messages)
        entries_equal = all([e1 == e2 for e1,e2 in zip(self.messages, other.messages)])

        doc_lens_eq = len(self.docs) == len(other.docs)
        docs_equal = all([d1 == d2 for d1,d2 in zip(self.docs, other.docs)])

        return entry_lens_eq and entries_equal and doc_lens_eq and docs_equal
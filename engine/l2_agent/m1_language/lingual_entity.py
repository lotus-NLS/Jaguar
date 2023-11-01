from __future__ import annotations

from threading import Thread
from typing import Optional, List
from abc import abstractmethod
from pyutils import DaemonThread
from queue import Queue

from .language_types import Entry, DialogueRole, Flag
from .channel import ChannelInterface as Channel

# ----------------------------------------------------


class LingualEntity:
    def __init__(self, role : DialogueRole, name : Optional[str] = None):
        super().__init__()
        self._role : DialogueRole = role
        self.name : str = name if not name is None else self._role
        self._personal_log : list[Entry] = []

        self.channel : Optional[Channel] = None
        self.to_say : Queue[Entry] = Queue()
        DaemonThread(target=self.speaking_routine).start()


    def clear_log(self):
        self._personal_log = []

    def get_unread_entries(self) -> list[Entry]:
        return [entry for entry in self._personal_log if not entry.get_is_processed()]

    # ------------------------------
    # Speak

    def enqueue_msg(self, msg: str, flags: Optional[List[Flag]] = None):
        self.to_say.put(Entry(role=self._role, msg=msg, flags=flags))

    def speaking_routine(self):
        while True:
            self.do_speak(self.to_say.get())

    def do_speak(self, new_entry):
        if self.channel is None:
            return

        if self.channel.speaker_staff.holder != self:
            self.channel.acquire_staff(holder=self)

        self.channel.broadcast(new_entry)
        self.channel.reset_return_countdown()

    # ------------------------------
    # Listen


    def process_entry(self, new_entry : Entry):
        if self.get_is_new_entry(partial_entry=new_entry):
            self._personal_log.append(new_entry)
            Thread(target=self.react, args=(new_entry,)).start()

        else:
            last_entry = self._personal_log[-1]
            last_entry.append_content(new_entry.get_content())


    def get_is_new_entry(self, partial_entry) -> bool:
        role, name, msg, flags = partial_entry.get_role(), partial_entry.get_name(), partial_entry.get_content(), partial_entry.get_flags()
        is_continuation = False
        if len(self._personal_log) > 0:
            last_entry = self._personal_log[-1]
            is_continuation = role == last_entry.get_role() and name == last_entry.get_name()

        return not is_continuation


    @abstractmethod
    def react(self, entry : Entry):
        pass

    # ------------------------------
    # log

    def think(self, msg: str):
        to_log = f'## Internal monologue: {msg}'
        new_entry = Entry(msg=to_log, role=self._role, name=self.name)
        return self.process_entry(new_entry=new_entry)

    def log_tool_msg(self, msg: str, tool_name: str):
        print(f'[Debug]: Tool {tool_name}: {msg}')
        return self.process_entry(new_entry=Entry(msg=msg, role=DialogueRole.tool_role(), name=tool_name))


    def log_system_msg(self, msg: str):
        return self.process_entry(new_entry=Entry(msg=msg, role=DialogueRole.system_role()))



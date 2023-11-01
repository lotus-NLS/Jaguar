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
        self.current_entry : Optional[Entry] = None

        self.channel : Optional[Channel] = None
        self.to_say : Queue[Entry] = Queue()
        DaemonThread(target=self.speaking_routine).start()


    def clear_log(self):
        self._personal_log = []

    def get_unread_entries(self) -> list[Entry]:
        return [entry for entry in self._personal_log if not entry.get_is_processed()]

    # ------------------------------
    # Speak

    def enqueue_partial(self, msg: str, flags: Optional[List[Flag]] = None):
        if flags is None:
            flags = []
        self.to_say.put(Entry(role=self._role, msg=msg, flags=flags))

    def enqueue_line(self, msg: str, flags: Optional[List[Flag]] = None):
        if flags is None:
            flags = []

        flags.append(Flag.get_entry_end_flag())
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

    def process_entry(self, new_entry: Entry):
        self.logger(new_entry=new_entry)
        if self.current_entry is None:
            self.current_entry = new_entry
            self._personal_log.append(new_entry)
        else:
            self.current_entry.append_content(additional_content=new_entry.get_content())


        if Flag.get_entry_end_flag() in new_entry.get_flags():
            self.current_entry = None
            Thread(target=self.react, args=(new_entry,)).start()


    @abstractmethod
    def logger(self, new_entry : Entry):
        pass


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



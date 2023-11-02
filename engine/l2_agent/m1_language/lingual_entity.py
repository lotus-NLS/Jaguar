from __future__ import annotations

from typing import Optional, List
from abc import abstractmethod
from pyutils import DaemonThread
from queue import Queue

from api.base.language_types import Entry, DialogueRole, Flag
from .channel import ChannelInterface as Channel

# ----------------------------------------------------

class LingualEntity:
    def __init__(self, role : DialogueRole, name : Optional[str] = None):
        super().__init__()
        self._role : DialogueRole = role
        self.name : str = name if not name is None else self._role

        self._personal_log : list[Entry] = []
        self.current_entry : Optional[Entry] = None
        self.entries_to_say : Queue[Entry] = Queue()

        self.channel : Optional[Channel] = None
        DaemonThread(target=self.speaking_routine).start()


    def clear_log(self):
        self._personal_log = []

    def get_unread_entries(self) -> list[Entry]:
        return [entry for entry in self._personal_log if not entry.get_is_processed()]

    # ------------------------------
    # Speak

    def enqueue(self, msg: str, flags: Optional[List[Flag]] = None, final : bool = True):
        if flags is None:
            flags = []

        if final:
            flags.append(Flag.get_entry_end_flag())

        self.entries_to_say.put(Entry(role=self._role, msg=msg, flags=flags))


    def speaking_routine(self):
        while True:
            new_entry = self.entries_to_say.get()
            if self.channel is None:
                return

            if self.channel.speaker_staff.holder != self:
                self.channel.acquire_staff(holder=self)

            self.channel.broadcast(new_entry)
            self.channel.reset_return_countdown()

    # ------------------------------
    # Listen and react

    def process_entry(self, new_entry: Entry):
        self.logger(new_entry=new_entry)
        if self.current_entry is None:
            self.current_entry = new_entry
            self._personal_log.append(new_entry)
        else:
            self.current_entry.append_content(additional_content=new_entry.get_content())


        if Flag.get_entry_end_flag() in new_entry.get_flags():
            self.current_entry = None
            DaemonThread(target=self.react, args=(new_entry,)).start()


    def logger(self, new_entry : Entry):
        pass

    @abstractmethod
    def react(self, entry : Entry):
        pass

    # ------------------------------
    # log

    def process_entry_from_info(self,msg : str, role : DialogueRole,name : str = '', flags : Optional[list[Flag]] = None):
        self.process_entry(Entry(msg=msg,role=role,name=name,flags=flags))

    def think(self, msg: str):
        return self.process_entry_from_info(msg=f'## Internal monologue: {msg}',role=self._role)

    def log_tool_msg(self, msg: str, tool_name: str):
        print(f'[Debug]: Tool {tool_name}: {msg}')
        return self.process_entry_from_info(msg=msg, role=DialogueRole.tool_role(), name=tool_name)

    def log_system_msg(self, msg: str):
        return self.process_entry_from_info(msg=msg, role=DialogueRole.system_role())



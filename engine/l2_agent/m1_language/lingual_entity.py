from __future__ import annotations

import copy
import logging
from typing import Optional
from abc import abstractmethod

from pyutils import DaemonThread
from queue import Queue

from api import Entry, DialogueRole, FlagContainer, Flag
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

    @staticmethod
    def print_entries(entries : list[Entry]):
        total_log = ''
        for entry in entries:
            total_log += str(entry)
        logging.info(total_log)

    def clear_log(self):
        self._personal_log = []

    def get_unread_entries(self) -> list[Entry]:
        return [entry for entry in self._personal_log if not entry.get_is_processed()]

    # ------------------------------
    # Speak

    def enqueue(self, msg: str, arg_flags: Optional[FlagContainer] = None, final : bool = False):
        new_entry = Entry(role=self._role, msg=msg, flags=arg_flags, is_final=final)
        self.entries_to_say.put(new_entry)


    def speaking_routine(self):
        while True:
            new_entry = self.entries_to_say.get()
            if self.channel is None:
                return

            if self.channel.speaker_staff.holder != self:
                self.channel.acquire_staff(holder=self)

            self.channel.broadcast(entry=new_entry)
            self.channel.reset_return_countdown()

    # ------------------------------
    # Listen and react

    def process_entry(self, new_entry: Entry):
        self.logger(new_entry=new_entry)

        if self.current_entry is None:
            self.current_entry = copy.copy(new_entry)
            self._personal_log.append(self.current_entry)
        else:
            self.current_entry.append_content(to_add=new_entry.get_content())

        if new_entry.flags.get(flag=Flag.IS_ENTRY_END):
            self.current_entry = None
            DaemonThread(target=self.react, args=(new_entry,)).start()


    def logger(self, new_entry : Entry):
        pass

    @abstractmethod
    def react(self, entry : Entry):
        pass

    # ------------------------------
    # log

    def process_entry_from_info(self,msg : str, role : DialogueRole,name : str = '', flags : FlagContainer = FlagContainer.make_default()):
        self.process_entry(Entry(msg=msg,role=role,name=name,flags=flags))

    def think(self, msg: str):
        return self.process_entry_from_info(msg=f'## Internal monologue: {msg}',role=self._role)

    def log_tool_msg(self, msg: str, tool_name: str):
        logging.info(f'Tool {tool_name}: {msg}')
        return self.process_entry_from_info(msg=msg, role=DialogueRole.tool_role(), name=tool_name)

    def log_system_msg(self, msg: str):
        return self.process_entry_from_info(msg=msg, role=DialogueRole.system_role())



from __future__ import annotations

from threading import Thread
from typing import Optional, List
from abc import abstractmethod
from pyutils import Countdown, DaemonThread
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


    def enqueue_msg(self, msg: str, flags: Optional[List[Flag]] = None):
        self.to_say.put(Entry(role=self._role, msg=msg, flags=flags))


    def speaking_routine(self):
        while True:
            if not self.channel is None:
                self.do_speak(self.to_say.get())


    def do_speak(self, new_entry):
        if self.channel.speaker_staff.holder != self:
            self.channel.acquire_staff(holder=self)

        self.channel.broadcast(new_entry)
        self.channel.reset_return_countdown()

    # ------------------------------
    # Update

    def clear_log(self):
        self._personal_log = []

    def get_unread_entries(self) -> list[Entry]:
        return [entry for entry in self._personal_log if not entry.get_is_processed()]

    # ------------------------------
    # Speak and react

    def process_partial_entry(self, partial_entry : Entry):
        role,name,msg,flags = partial_entry.get_role(), partial_entry.get_name(), partial_entry.get_content(), partial_entry.get_flags()

        if self.get_is_new_entry(partial_entry=partial_entry):
            new_entry = Entry(msg=msg, role=role, name=name, flags=flags)
            if not new_entry.get_role() == DialogueRole.user_role():
                new_entry.mark_processed()

            self._personal_log.append(new_entry)
            Thread(target=self.react, args=(new_entry,)).start()

        else:
            last_entry = self._personal_log[-1]
            last_entry.append_content(msg)


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


    def think(self, msg: str):
        to_log = f'## Internal monologue: {msg}'
        # print(f'[Debug]: {self._role} thought: {}')
        new_entry = Entry(msg=to_log, role=self._role, name=self.name)
        return self.process_partial_entry(partial_entry=new_entry)


    # ------------------------------
    # log

    def log_user_msg(self, msg: str):
        new_entry = Entry(msg=msg, role=DialogueRole.user_role())
        return self.process_partial_entry(partial_entry=new_entry)


    def log_tool_msg(self, msg: str, tool_name: str):
        print(f'[Debug]: Tool {tool_name}: {msg}')
        new_entry = Entry(msg=msg, role=DialogueRole.tool_role(), name=tool_name)
        return self.process_partial_entry(partial_entry=new_entry)


    def log_system_msg(self, msg: str):
        print(f'[Debug]: System: {msg}')
        new_entry = Entry(msg=msg, role=DialogueRole.system_role())
        return self.process_partial_entry(partial_entry=new_entry)



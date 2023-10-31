from __future__ import annotations

from threading import Thread
from typing import Optional, List
from abc import abstractmethod
from pyutils import Countdown, DaemonThread
from queue import Queue

from .channel import Channel, Stream
from .entry import Entry, DialogueRole, Flag


# ----------------------------------------------------


class LingualEntity:
    def __init__(self, role : DialogueRole, name : Optional[str] = None):
        super().__init__()
        self._role : DialogueRole = role
        self._personal_log : list[Entry] = []
        self._channel : Optional[Channel] = None
        self.name = name if not name is None else self._role
        self.stream : Optional[Stream] = None

        self.staff_countdown : Countdown = Countdown(time_to_finish=0.5, on_countdown_finish=self.try_release_staff)
        self.to_say : Queue[Entry] = Queue()
        DaemonThread(target=self.do_speak).start()


    def speak(self, msg: str, flags: Optional[List[Flag]] = None):
        self.to_say.put(Entry(role=self._role, msg=msg, flags=flags))


    def do_speak(self):
        while True:
            new_entry = self.to_say.get()
            flags = new_entry.flags
            if self._channel is None:
                return

            if self._channel.speaker_staff.holder != self:
                self._channel.acquire_staff(holder=self)

            self._channel.broadcast(new_entry)
            self.staff_countdown.relaunch()

            if not flags is None:
                self.try_release_staff() if Flag.get_entry_end_flag() in flags else None


    def try_release_staff(self):
        print(f'[Debug]: The staff has been released from {self.name}')
        try:
            self._channel.release_staff()
        except:
            pass

    # ------------------------------
    # Update

    def clear_log(self):
        self._personal_log = []

    def start_listen(self, channel : Channel):
        Thread(target=self.listen_to_channel, args=(channel,),daemon=True).start()

    def listen_to_channel(self, channel : Channel):
        self._channel = channel
        if not self.stream is None:
            self.leave_channel()

        self.stream = channel.get_stream()
        while True:
            entry = self.stream.get()
            if entry is None:
                break

            self._process_partial_entry(partial_entry=entry)


    def leave_channel(self):
        self.stream.close()
        self._channel = None

    def get_unread_entries(self) -> list[Entry]:
        return [entry for entry in self._personal_log if not entry.get_is_read()]

    # ------------------------------
    # Speak and react

    def _process_partial_entry(self, partial_entry : Entry):
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
        return self._process_partial_entry(partial_entry=new_entry)


    # ------------------------------
    # log

    def log_user_msg(self, msg: str):
        new_entry = Entry(msg=msg, role=DialogueRole.user_role())
        return self._process_partial_entry(partial_entry=new_entry)


    def log_tool_msg(self, msg: str, tool_name: str):
        print(f'[Debug]: Tool {tool_name}: {msg}')
        new_entry = Entry(msg=msg, role=DialogueRole.tool_role(), name=tool_name)
        return self._process_partial_entry(partial_entry=new_entry)


    def log_system_msg(self, msg: str):
        print(f'[Debug]: System: {msg}')
        new_entry = Entry(msg=msg, role=DialogueRole.system_role())
        return self._process_partial_entry(partial_entry=new_entry)



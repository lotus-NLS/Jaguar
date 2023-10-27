from __future__ import annotations
from threading import Thread
from typing import Union, Optional
from abc import abstractmethod
# from engine.l3_settings.m2_OperatorIO import user_io

from .channel import Channel
from .entry import Entry, DialogueRole, Flag


# ----------------------------------------------------

class LingualEntity:
    def __init__(self, role : DialogueRole, name : Optional[str] = None):
        super().__init__()
        self._role : DialogueRole = role
        self._personal_log : list[Entry] = []
        self._channel : Union[Channel, None] = None
        self.name = name if not name is None else self._role

    # ------------------------------
    # Update

    def clear_log(self):
        self._personal_log = []


    def join_channel(self, channel : Channel):
        self.leave_channel()
        self._channel  = channel
        self._channel.listener_loggers.append(self._process_partial_entry)


    def leave_channel(self):
        if not self._channel is None:
            try:
                self._channel.listener_loggers.remove(self._process_partial_entry)
            except:
                print(f'[Debug]: Could not find personal logger in channel {self._channel}')
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


    def speak(self, msg : str, flags : Optional[list[Flag]] = None):
        if self._channel is None:
            return
        self._channel.broadcast_message(Entry(role=self._role, msg=msg,flags=flags))

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



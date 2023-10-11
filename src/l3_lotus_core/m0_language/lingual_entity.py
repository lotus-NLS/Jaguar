from __future__ import annotations
from threading import Thread
from typing import Union, Optional
from abc import abstractmethod
from src.l3_lotus_core.m2_OperatorIO import user_io

from src.l3_lotus_core.m0_language.channel import Channel
from src.l3_lotus_core.m0_language.entry import Entry, DialogueRole, Flags


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

    def join_channel(self, channel : Channel):
        self.leave_channel()
        self._channel  = channel
        self._channel.listener_loggers.append(self._log_entry)

    def leave_channel(self):
        if not self._channel is None:
            try:
                self._channel.listener_loggers.remove(self._log_entry)
            except:
                print(f'[Debug]: Could not find personal logger in channel {self._channel}')
            self._channel = None

    def get_unread_entries(self) -> list[Entry]:
        return [entry for entry in self._personal_log if not entry.get_is_read()]

    # ------------------------------
    # log

    def _log_entry(self, entry : Entry):
        if not entry.get_role() == DialogueRole.user_role():
            entry.mark_processed()

        self._personal_log.append(entry)
        Thread(target=self.react, args=(entry,)).start()


    def log_user_msg(self, msg : str):
        self._log_entry(Entry(role=DialogueRole.user_role(), msg=msg))


    def log_tool_msg(self, msg : str, tool_name : str = 'undefined_tool'):
        print(f'[Debug]: {self._role} read: {msg}')
        self._log_entry(entry=Entry(role=DialogueRole.tool_role(), msg=msg, tool_name= tool_name))


    def log_system_msg(self,msg : str):
        self._log_entry(Entry(role=DialogueRole.system_role(), msg=msg))

    # ------------------------------
    # Speak and react

    @abstractmethod
    def react(self, entry : Entry):
        pass

    def think(self, msg : str, verbose = True):
        the_msg = f'## Internal monologue: {msg}'
        if verbose:
            print(f'[Debug]: {self._role} thought: {the_msg}')
        self._log_entry(entry=Entry(role=self._role, msg=the_msg))


    def speak(self, msg : str, flags : Optional[Flags] = None):
        if self._channel is None:
            return

        print(f'[Debug]: {self._role} said: {msg}')
        self._channel.broadcast_message(Entry(role=self._role, msg=msg,flags=flags))

    # ------------------------------
    # Other

    def retrieve_user_permission(self, request_msg : str) -> bool:
        self.speak(msg=f'{request_msg} (y/n)')
        user_approves = user_io.get_confirmation()

        if user_approves:
            self.think(f'User confirmed permission')
        else:
            self.think(f'User denied permission')
        return user_approves

    @staticmethod
    def enter_into_channel(channel : Channel, channel_members : list[LingualEntity]):
        for participant in channel_members:
            participant.join_channel(channel)


from __future__ import annotations
from threading import Thread
from typing import Union, Optional
from abc import abstractmethod
from src.l3_lotus_core.m2_OperatorIO import user_io

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
        self._channel.listener_loggers.append(self._log_partial_entry)

    def leave_channel(self):
        if not self._channel is None:
            try:
                self._channel.listener_loggers.remove(self._log_info)
            except:
                print(f'[Debug]: Could not find personal logger in channel {self._channel}')
            self._channel = None

    def get_unread_entries(self) -> list[Entry]:
        return [entry for entry in self._personal_log if not entry.get_is_read()]

    # ------------------------------
    # log


    def _log_partial_entry(self, partial_entry : Entry):
        role,name,msg,flags = partial_entry.get_role(), partial_entry.get_name(), partial_entry.get_content(), partial_entry.get_flags()
        is_same_entity = False

        last_entry = None
        if len(self._personal_log) > 0:
            last_entry = self._personal_log[-1]
            is_same_entity = role == last_entry.get_role() and name == last_entry.get_name()

        if not last_entry is None and is_same_entity:
            last_entry.append_content(msg)
        else:
            new_entry = Entry(msg=msg, role=role, name=name, flags=flags)
            if not new_entry.get_role() == DialogueRole.user_role():
                new_entry.mark_processed()

            self._personal_log.append(new_entry)
            Thread(target=self.react, args=(new_entry,)).start()


    def _log_info(self, msg : str, role : DialogueRole, name : Optional[str] = None, flags : Optional[list[Flag]] = None):
        self._log_partial_entry(partial_entry=Entry(msg=msg, role=role, name=name, flags=flags))


    def log_user_msg(self, msg : str):
        return self._log_info(msg=msg, role=DialogueRole.user_role())


    def log_tool_msg(self, msg : str, tool_name : str):
        print(f'[Debug]: {self._role} read: {msg}')
        self._log_info(msg=msg, role=DialogueRole.tool_role(), name=tool_name)


    def log_system_msg(self,msg : str):
        self._log_info(msg=msg, role=DialogueRole.system_role())

    # ------------------------------
    # Speak and react

    @abstractmethod
    def react(self, entry : Entry):
        pass

    def think(self, msg : str, verbose = True):
        the_msg = f'## Internal monologue: {msg}'
        if verbose:
            print(f'[Debug]: {self._role} thought: {the_msg}')
        self._log_info(msg=msg, role=self._role, name=self.name)


    def speak(self, msg : str, flags : Optional[list[Flag]] = None):
        if self._channel is None:
            return

        # print(f'[Debug]: {self._role} said: {msg}')
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


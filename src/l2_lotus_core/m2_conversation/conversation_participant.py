from __future__ import annotations
from threading import Thread
from typing import Union, Optional


from src.l2_lotus_core.m2_conversation.channel import Channel
from src.l2_lotus_core.m2_conversation.conversation_entry import ConversationEntry, DialogueRole

# ----------------------------------------------------

class ConversationParticipant:
    def __init__(self, role : DialogueRole, name : Optional[str] = None):
        super().__init__()
        self._role : DialogueRole = role
        self._personal_log : list[ConversationEntry] = []
        self._channel : Union[Channel, None] = None
        self.name = name if not name is None else self._role

    # ------------------------------
    # Update

    def join_channel(self, channel : Channel):
        self.leave_channel()
        self._channel  = channel
        self._channel.listener_loggers.append(self._log_entry)

    def leave_channel(self) -> None:
        if not self._channel is None:
            try:
                self._channel.listener_loggers.remove(self._log_entry)
            except:
                print(f'[Debug]: Could not find personal logger in channel {self._channel}')
            self._channel = None

    # ------------------------------
    # Speak and react

    def _log_entry(self, entry : ConversationEntry):
        self._personal_log.append(entry)
        Thread(target=self.react, args=(entry,)).start()

    def log_user_msg(self, msg : str):
        self._log_entry(ConversationEntry(role=DialogueRole.c_user(), msg=msg))

    def log_tool_msg(self, msg : str, tool_name : str = 'undefined_tool'):
        print(f'[Debug]: {self._role} read: {msg}')
        self._log_entry(entry=ConversationEntry(role=DialogueRole.c_tool(), msg=msg, tool_name= tool_name))

    def log_system_msg(self,msg : str):
        self._log_entry(ConversationEntry(role=DialogueRole.c_system(), msg=msg))

    def react(self, conv_entry : ConversationEntry):
        pass

    def think(self, msg : str, verbose = True):
        the_msg = f'## Internal monologue: {msg}'
        if verbose:
            print(f'[Debug]: {self._role} thought: {the_msg}')
        self._log_entry(entry=ConversationEntry(role=self._role, msg=the_msg))


    def speak(self, msg : str):
        if self._channel is None:
            return

        print(f'[Debug]: {self._role} said: {msg}')
        self._channel.broadcast_message(ConversationEntry(role=self._role, msg=msg))

    # ------------------------------
    # Other

    @staticmethod
    def make_entry(role : DialogueRole, msg : str):
        return ConversationEntry(role,msg)

    @staticmethod
    def enter_into_channel(channel : Channel, participant_list : list[ConversationParticipant]):
        for participant in participant_list:
            participant.join_channel(channel)

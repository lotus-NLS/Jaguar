from __future__ import annotations
import threading
from typing import Union

from src.l5_conversation.l1_channel import Channel
from src.l5_conversation.l2_conversation_entry import ConversationEntry, DialogueRole


# Conversation:
# -> Only Conversation Particpants can join a l5_conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------


# TODO: Log entry should not be exposed downstream. Instead use special loggers; Neither should Conversation entry be used
class ConversationParticipant:
    def __init__(self, role : DialogueRole):
        super().__init__()
        self._role : DialogueRole = role
        self._personal_log : list[ConversationEntry] = []
        self._channel : Union[Channel, None] = None

    # ------------------------------
    # Update

    def join_channel(self, channel : Channel):
        self.leave_channel()
        self._channel  = channel
        self._channel.participant_loggers.append(self._log_entry)

    def leave_channel(self) -> None:
        if not self._channel is None:
            try:
                self._channel.participant_loggers.remove(self._log_entry)
            except:
                print(f'[Debug]: Could not find personal logger in channel {self._channel}')
            self._channel = None

    # ------------------------------
    # Speak and react

    def _log_entry(self, entry : ConversationEntry):
        self._personal_log.append(entry)
        threading.Thread(target=self._reaction_protocol, kwargs=({'dialogue_line' : entry})).start()

    def _reaction_protocol(self, dialogue_line : ConversationEntry):
        pass

    def log_user_msg(self, msg):
        self._log_entry(ConversationEntry(role=DialogueRole.user(), msg=msg))

    def log_tool_msg(self, msg : str, tool_name : str = 'undefined_tool'):
        print(f'[Debug]: {self._role} read: {msg}')
        self._log_entry(entry=ConversationEntry(role=DialogueRole.tool(), msg=msg, tool_name= tool_name))

    def think(self, msg : str):
        the_msg = f'## Internal monologue: {msg}'
        print(f'[Debug]: {self._role} thought: {the_msg}')
        self._log_entry(entry=ConversationEntry(role=self._role, msg=the_msg))

    def speak(self, msg : str):
        if self._channel is None:
            return

        print(f'[Debug]: {self._role} said: {msg}')
        self._channel.broadcast_message(ConversationEntry(role=self._role, msg=msg))

    # ------------------------------
    # Log

    @staticmethod
    def get_entry(role : DialogueRole, msg : str):
        return ConversationEntry(role,msg)

    def get_memory(self):
        return self._personal_log

    @staticmethod
    def enter_into_conversation(channel : Channel, participant_list : list[ConversationParticipant]):
        for participant in participant_list:
            participant.join_channel(channel)

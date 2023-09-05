import threading
from typing import List, Union

from s4_conversation.s1_Channel import Channel
from s4_conversation.s2_ConversationEntry import ConversationEntry
from s4_conversation.s3_DialogueRoles import DialogueRole

# Conversation:
# -> Only Conversation Particpants can join a s4_conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------


class ConversationParticipant:
    def __init__(self, role : DialogueRole):
        super().__init__()
        self._role : DialogueRole = role
        self._personal_log : List[ConversationEntry] = []
        self._channel : Union[Channel, None] = None

    # ------------------------------
    # Update

    def join_channel(self, channel : Channel):
        self.leave_channel()
        self._channel  = channel
        self._channel.participant_loggers.append(self.log_entry)

    def leave_channel(self) -> None:
        if not self._channel is None:
            try:
                self._channel.participant_loggers.remove(self.log_entry)
            except:
                print(f'[Debug]: Could not find personal logger in channel {self._channel}')
            self._channel = None

    # ------------------------------
    # Speak and react

    def log_entry(self, entry : ConversationEntry):
        self._personal_log.append(entry)
        threading.Thread(target=self._reaction_protocol, kwargs=({'dialogue_line' : entry})).start()

    def _reaction_protocol(self, dialogue_line : dict):
        pass

    def read(self,msg : str, tool_name : str):
        print(f'[Debug]: {self._role} read: {msg}')
        self.log_entry(entry=ConversationEntry(role=DialogueRole.tool(), msg=msg, tool_name= tool_name))

    def think(self,msg : str):
        the_msg = f'## Internal monologue: {msg}'
        print(f'[Debug]: {self._role} thought: {the_msg}')
        self.log_entry(entry=ConversationEntry(role=self._role, msg=the_msg))

    def speak(self, msg : str):
        if self._channel is None:
            return

        print(f'[Debug]: {self._role} said: {msg}')
        self._channel.broadcast_message(ConversationEntry(role=self._role, msg=msg))

    # ------------------------------
    # Log

    def get_memory(self):
        return self._personal_log


def enter_into_conversation(channel : Channel, participant_list : list[ConversationParticipant]):
    for participant in participant_list:
        participant.join_channel(channel)

from typing import List
from s1_conversation.Conversation_Entry import Conversation_Entry
from s1_conversation.Participant import Conversation_Participant

# Conversation:
# -> Only Conversation Particpants can join a s1_conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------
from s4_tests.test_conversation import speak_and_think


class ReactiveList(list):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def append(self, item):
        super().append(item)
        if self.callback:
            self.callback(item)


class Conversation:
    def __init__(self):
        self._participants : List[Conversation_Participant] = []

    def add_participant(self, participant  : Conversation_Participant):
        if not isinstance(participant, Conversation_Participant):
            print(f'Given object is not a Conversation_Participant. Aborting add_participant routine ...')
            return

        participant.broadcast = self.broadcast_message
        self._participants.append(participant)

    def broadcast_message(self, role : str, msg : str):
        print(f'[Debug]: {role} said: {msg}')

        for participant in self._participants:
            participant._conversational_memory.append(Conversation_Entry(role=role, msg=msg))

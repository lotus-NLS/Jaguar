from typing import List, Callable
from s1_conversation.Conversation_Entry import Conversation_Entry

# Conversation:
# -> Only Conversation Particpants can join a s1_conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------
from s1_conversation.Roles import Dialogue_Roles
from s4_tests.test_conversation import speak_and_think


class ReactiveList(list):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def append(self, item : object):
        super().append(item)
        if self.callback:
            self.callback(item)


class Conversation_Participant:
    def __init__(self, role : str):
        if not role in Dialogue_Roles.as_list():
            print(f'[Debug]: Given role is not part of the allowed roles {Dialogue_Roles.as_list()}')
            return

        self.role : str = role
        self.broadcast : Callable = lambda *args, **kwargs: None
        self.conversational_memory : ReactiveList[Conversation_Entry] = ReactiveList(callback=self._react)

    def register_system_message(self, msg : str):
        self.conversational_memory.append(Conversation_Entry(role=Dialogue_Roles.system, msg=msg))

    def think(self,msg : str):
        print(f'[Debug]:{self.role} thought: {msg}')

        self.conversational_memory.append(Conversation_Entry(role=self.role, msg=msg))

    def speak(self, message : str):
        self.broadcast(self.role, message)

    def _react(self, dialogue_line : dict):
        pass

    def print_memory(self):
        print(self.conversational_memory)

class Conversation:
    def __init__(self):
        self._participants : List[Conversation_Participant] = []

    def add_participant(self, participant  : Conversation_Participant):
        if not isinstance(participant, Conversation_Participant):
            print(f'Given object is not a Conversation_Participant. Aborting add_participant routine ...')
            return

        participant.broadcast = self.broadcast_message
        self._participants.append(participant)


    # TODO: Change the argument to conversation entry
    def broadcast_message(self, role : str, msg : str):
        print(f'[Debug]: {role} said: {msg}')

        for participant in self._participants:
            participant.conversational_memory.append(Conversation_Entry(role=role, msg=msg))



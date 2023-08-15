from typing import Callable

from s1_conversation.Conversation import ReactiveList
from s1_conversation.Conversation_Entry import Conversation_Entry
from s1_conversation.Roles import Dialogue_Roles

# ---------------------------------------------------------

class Conversation_Participant:
    def __init__(self, role : str):
        if not role in Dialogue_Roles.as_list():
            print(f'[Debug]: Given role is not part of the allowed roles {Dialogue_Roles.as_list()}')
            return

        self.role = role
        self.broadcast : Callable = lambda *args, **kwargs: None
        self._conversational_memory : ReactiveList[Conversation_Entry] = ReactiveList(callback=self._react)

    def register_system_message(self, msg : str):
        self._conversational_memory.append(Conversation_Entry(role=Dialogue_Roles.system, msg=msg))

    def think(self,msg : str):
        print(f'[Debug]:{self.role} thought: {msg}')

        self._conversational_memory.append(Conversation_Entry(role=self.role, msg=msg))

    def speak(self, message : str):
        self.broadcast(self.role, message)

    def _react(self, dialogue_line : dict):
        pass

    def print_memory(self):
        print(self._conversational_memory)
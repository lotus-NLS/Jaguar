import queue, threading
from queue import Queue
from typing import List, Callable


# Conversation:
# -> Only Conversation Particpants can join a s1_conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------

class Dialogue_Roles:
    user = 'user'
    agent = 'assistant'
    system = 'system'

    @classmethod
    def as_list(cls):
        as_list = []
        for name, value in cls.__dict__.items():
            if not name.startswith("__"):
                as_list.append(value)
        return as_list


class ConversationEntry(dict):
    def __init__(self,role : str, msg : str):
        super().__init__()

        if not role in Dialogue_Roles.as_list():
            print(f'[Debug]: Given role {role} is not part of the allowed roles {Dialogue_Roles.as_list()}. Defaulting to agent role ...')
            self['role'] = Dialogue_Roles.agent
        else:
            self['role'] = role

        self['content'] = msg

    def get_role(self):
        return self['role']

    def get_content(self):
        return self['content']


class ConversationParticipant:
    def __init__(self, role : str):
        if not role in Dialogue_Roles.as_list():
            print(f'[Debug]: Given role {role} is not part of the allowed roles {Dialogue_Roles.as_list()}'
                  f'Defaulting to the agent role')
            self._role = Dialogue_Roles.agent
        else:
            self._role : str = role

        self._broadcast : Callable = lambda *args, **kwargs: None
        self._conversational_memory : List[ConversationEntry] = []

    def register_entry(self, entry : ConversationEntry):
        self._conversational_memory.append(entry)
        threading.Thread(target=self._reaction_protocol, kwargs=({'dialogue_line' : entry})).start()

    def think(self,msg : str):
        print(f'[Debug]:{self._role} thought: {msg}')
        self.register_entry(entry=ConversationEntry(role=self._role,msg=msg))

    def speak(self, msg : str):
        print(f'[Debug]: {self._role} said: {msg}')
        self._broadcast(ConversationEntry(role=self._role, msg=msg))

    def _reaction_protocol(self, dialogue_line : dict):
        pass

    def print_memory(self):
        print(self._conversational_memory)


class Conversation:
    def __init__(self, participant_list : List[ConversationParticipant]):
        self._participants: List[ConversationParticipant] = []
        for participant in participant_list:
            self.add_participant(participant)

        self._message_queue : Queue[ConversationEntry] = queue.Queue()
        threading.Thread(target=self._process_queue).start()

    def add_participant(self, participant  : ConversationParticipant):
        if not isinstance(participant, ConversationParticipant):
            print(f'Given object is not a Conversation_Participant. Aborting add_participant routine ...')
            return

        participant._broadcast = self._broadcast_message
        self._participants.append(participant)

    def _process_queue(self):
        while True:
            entry = self._message_queue.get()
            for participant in self._participants:
                participant.register_entry(entry)


    def _broadcast_message(self, entry : ConversationEntry):
        self._message_queue.put(entry)

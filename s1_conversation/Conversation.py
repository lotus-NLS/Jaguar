import queue
import threading
from typing import List, Callable


# Conversation:
# -> Only Conversation Particpants can join a s1_conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------



class ReactiveList(list):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def append(self, item : object):
        super().append(item)
        if self.callback:
            self.callback(item)


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


class Conversation_Entry(dict):
    def __init__(self,role : str, msg : str):
        super().__init__()

        if not role in Dialogue_Roles.as_list():
            print(f'[Debug]: Given role {role} is not part of the allowed roles {Dialogue_Roles.as_list()}. Defaulting to agent role ...')
            self['role'] = Dialogue_Roles.agent
        else:
            self['role'] = role

        if not isinstance(msg,str):
            print(f'[Debug]: Given message {msg} is not a string. Typecasting msg object to string to include as message content ...')
            self['content'] = str(msg)

        else:
            self['content'] = msg


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

        thought_msg = f'## Internal Assistant Log\n' \
                      f'{msg}'

        self.conversational_memory.append(Conversation_Entry(role=self.role, msg=thought_msg))

    def speak(self, message : str):
        self.broadcast(self.role, message)

    def _reaction_protocol(self, dialogue_line : dict):
        pass

    def _react(self,dialogue_line : dict):
        threading.Thread(target=self._reaction_protocol,kwargs=({'dialogue_line' : dialogue_line})).start()

    def print_memory(self):
        print(self.conversational_memory)


class Conversation:
    def __init__(self):
        self._participants: List[Conversation_Participant] = []
        self._message_queue = queue.Queue()
        threading.Thread(target=self._process_queue).start()

    def add_participant(self, participant  : Conversation_Participant):
        if not isinstance(participant, Conversation_Participant):
            print(f'Given object is not a Conversation_Participant. Aborting add_participant routine ...')
            return

        participant.broadcast = self.broadcast_message
        self._participants.append(participant)


    def _process_queue(self):
        while True:
            role, msg = self._message_queue.get()
            print(f'[Debug]: {role} said: {msg}')
            for participant in self._participants:
                participant.conversational_memory.append(Conversation_Entry(role=role, msg=msg))

    # TODO: Change the argument to conversation entry
    def broadcast_message(self, role: str, msg: str):
        self._message_queue.put((role, msg))



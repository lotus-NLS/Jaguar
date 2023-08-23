import queue, threading
from queue import Queue
from typing import List, Callable, Union


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

        self._conversation : Union[Conversation,None] = None
        self._broadcast : Callable = lambda *args, **kwargs: None
        self._conversational_log : List[ConversationEntry] = []

    # ------------------------------
    # Update

    def join_conversation(self,conversation):
        self._conversation  = conversation
        self._broadcast = conversation.broadcast_message
        conversation.add_listener(self)

    def leave_conversation(self):
        self._broadcast = lambda *args, **kwargs: None
        self._conversation.remove_listener(self)

    # ------------------------------
    # Speak and react

    def log_entry(self, entry : ConversationEntry):
        self._conversational_log.append(entry)
        threading.Thread(target=self._reaction_protocol, kwargs=({'dialogue_line' : entry})).start()

    def think(self,msg : str):
        print(f'[Debug]:{self._role} thought: {msg}')
        self.log_entry(entry=ConversationEntry(role=self._role, msg=msg))

    def speak(self, msg : str):
        print(f'[Debug]: {self._role} said: {msg}')
        self._broadcast(ConversationEntry(role=self._role, msg=msg))

    def _reaction_protocol(self, dialogue_line : dict):
        pass

    # ------------------------------
    # Log

    def print_memory(self):
        print(self._conversational_log)



class Conversation:
    def __init__(self):
        self._listeners: List[ConversationParticipant] = []
        self._message_queue : Queue[ConversationEntry] = queue.Queue()

        self._is_running = True
        threading.Thread(target=self._process_queue).start()

    def stop(self):
        self._is_running = False

    def _process_queue(self):
        while self._is_running:
            try:
                entry = self._message_queue.get(block=True, timeout=1)  # Adjust timeout as needed
                for listener in self._listeners:
                    listener.log_entry(entry)
            except queue.Empty:
                pass  # Continue the loop if the queue is empty

    def remove_listener(self, participant : ConversationParticipant):
        self._listeners.remove(participant)

    def add_listener(self, participant  : ConversationParticipant):
        self._listeners.append(participant)

    def broadcast_message(self, entry : ConversationEntry):
        self._message_queue.put(entry)

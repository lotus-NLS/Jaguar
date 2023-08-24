import queue, threading
from queue import Queue
from typing import List, Callable, Union
from s1_conversation.CustomQueue import CustomQueue

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

        self._channel : Union[Channel, None] = None
        self._personal_log : List[ConversationEntry] = []

    # ------------------------------
    # Update

    def join_channel(self, conversation):
        self.leave_channel()
        self._channel  = conversation
        conversation.add_participant(self)

    def leave_channel(self) -> None:
        if not self._channel is None:
            self._channel.remove_particpant(self)
            self._channel = None

    # ------------------------------
    # Speak and react

    def log_entry(self, entry : ConversationEntry):
        self._personal_log.append(entry)
        threading.Thread(target=self._reaction_protocol, kwargs=({'dialogue_line' : entry})).start()

    def think(self,msg : str):
        print(f'[Debug]:{self._role} thought: {msg}')
        self.log_entry(entry=ConversationEntry(role=self._role, msg=msg))

    def speak(self, msg : str):
        if self._channel is None:
            return

        print(f'[Debug]: {self._role} said: {msg}')
        self._channel.broadcast_message(ConversationEntry(role=self._role, msg=msg))

    def _reaction_protocol(self, dialogue_line : dict):
        pass

    # ------------------------------
    # Log

    def print_memory(self):
        print(self._personal_log)


class Channel:
    def __init__(self):
        self._participants: List[ConversationParticipant] = []
        self._message_queue : Queue[ConversationEntry] = queue.Queue()
        self._is_running = True

        threading.Thread(target=self._process_queue).start()

    def stop(self):
        self._is_running = False

    def _process_queue(self):
        while self._is_running:
            try:
                entry = self._message_queue.get(block=True, timeout=1)  # Adjust timeout as needed
                for listener in self._participants:
                    listener.log_entry(entry)
            except queue.Empty:
                pass  # Continue the loop if the queue is empty

    def remove_particpant(self, participant : ConversationParticipant):
        try:
            self._participants.remove(participant)
        except:
            print(f'[Debug]: Tried to remove participant {participant} who is not listed in participants')

    def add_participant(self, participant  : ConversationParticipant):
        self._participants.append(participant)

    def broadcast_message(self, entry : ConversationEntry):
        self._message_queue.put(entry)

    def join_participants(self, participant_list : list[ConversationParticipant]):
        for participant in participant_list:
            participant.join_channel(self)

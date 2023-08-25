import queue, threading
from queue import Queue
from typing import List, Callable, Union
from s1_conversation.DialogueRoles import DialogueRole

# Conversation:
# -> Only Conversation Particpants can join a s1_conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------


class ConversationEntry(dict):
    def __init__(self,role : DialogueRole, msg : str):
        super().__init__()
        self['role'] = role
        self['content'] = msg

    def get_role(self):
        return self['role']

    def get_content(self):
        return self['content']


class Channel:
    def __init__(self):
        self.participant_loggers: list[Callable[[ConversationEntry], None]] = []
        self._message_queue : Queue[ConversationEntry] = queue.Queue()
        self._is_running = True

        threading.Thread(target=self._process_queue).start()

    # ------------------------------
    # Setup

    def _process_queue(self):
        while self._is_running:
            try:
                entry = self._message_queue.get(block=True, timeout=0.1)
                [logger(entry) for logger in self.participant_loggers]
            except queue.Empty:
                pass

    # ------------------------------
    # Other

    def broadcast_message(self, entry : ConversationEntry):
        self._message_queue.put(entry)

    def stop_after_next_timeout(self):
        self._is_running = False



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

    def think(self,msg : str):
        print(f'[Debug]:{self._role} thought: {msg}')
        self.log_entry(entry=ConversationEntry(role=self._role, msg=msg))

    def speak(self, msg : str):
        if self._channel is None:
            return

        print(f'[Debug]: {self._role} said: {msg}')
        self._channel.broadcast_message(ConversationEntry(role=self._role, msg=msg))

    # ------------------------------
    # Log

    def print_memory(self):
        print(self._personal_log)


def enter_into_conversation(channel : Channel, participant_list : list[ConversationParticipant]):
    for participant in participant_list:
        participant.join_channel(channel)

from typing import Callable,List

import logging
logger = logging.getLogger()

# ----------------------------------------------------

def get_dialogue_line(role,msg):
    return {"role": role, "content": msg}

# Those are the only three roles defined in the API. No other role can be introduced.
class Dialogue_Role:
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


class Conversation_Participant:
    def __init__(self, role : str):
        if not role in Dialogue_Role.as_list():
            logger.debug(f'Given role is not part of the allowed roles {Dialogue_Role.as_list()}')
            return

        self.role = role
        self.broadcast_list : List[Callable] = []
        self.conversational_memory : List[dict] = []

    def register_system_message(self, msg : str):
        self.conversational_memory.append(get_dialogue_line(Dialogue_Role.system,msg))

    def think(self,msg : str):
        # DEBUG
        print(f'{self.role} thought: {msg}')

        self.conversational_memory.append(get_dialogue_line(role=self.role,msg=msg))

    def speak(self, message : str):
        for broadcast in self.broadcast_list:
            broadcast(self.role, message)

    def print_memory(self):
        print(self.conversational_memory)


class Conversation:
    def __init__(self):
        self._participants = []

    def add_participant(self, participant  : Conversation_Participant):
        self._participants.append(participant)
        participant.broadcast_list.append(self.broadcast_message)

    def broadcast_message(self, role : str, msg : str):
        # DEBUG
        print(f'{role} said: {msg}')

        for participant in self._participants:
            participant : Conversation_Participant
            participant.conversational_memory.append({"role": role, "content": msg})


# ----------------------------------------------------
# Test driver code

# Create a handler
this_conversation = Conversation()

# Create participants and add them to the handler
participant1 = Conversation_Participant(role=Dialogue_Role.agent)
this_conversation.add_participant(participant1)

participant2 = Conversation_Participant(role=Dialogue_Role.agent)
this_conversation.add_participant(participant2)

# Participants write messages
participant1.speak('Hello from participant 1!')
participant2.speak('Hello from participant 2!')
participant2.think('I do not even want to say hello to that guy!')

# Participants print their logs
print("Logs for Participant1:")
participant1.print_memory()

print("Logs for Participant2:")
participant2.print_memory()
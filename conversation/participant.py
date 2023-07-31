from typing import Callable,List

import logging
logger = logging.getLogger()

class Roles:
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
    def __init__(self, role : str, broadcasts : List[Callable]):
        if not role in Roles.as_list():
            logger.debug(f'Given role is not part of the allowed roles {Roles.as_list()}')
            return

        self.role = role
        self.broadcast_list = broadcasts
        self.conversational_memory = []

    def speak(self, message : str):
        for broadcast in self.broadcast_list:
            broadcast(self.role, message)

    def print_memory(self):
        print(self.conversational_memory)

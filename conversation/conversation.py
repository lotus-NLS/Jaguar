from typing import Callable,List

import logging
logger = logging.getLogger()


# Conversation:
# -> Only Conversation Particpants can join a conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------

# Those are the only three roles defined in the API. No other role can be introduced.
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


class Dialgoue_line(dict):
    def __init__(self,role : str,msg : str):
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


class Reactive_List(list):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def append(self, item):
        super().append(item)
        if self.callback:
            self.callback(item)


class Conversation_Participant:
    def __init__(self, role : str):
        if not role in Dialogue_Roles.as_list():
            logger.debug(f'Given role is not part of the allowed roles {Dialogue_Roles.as_list()}')
            return

        self.role = role
        self.broadcast : Callable = lambda *args, **kwargs: None
        self.conversational_memory : Reactive_List[Dialgoue_line] = Reactive_List(callback=self.react)

    def register_system_message(self, msg : str):
        self.conversational_memory.append(Dialgoue_line(role=Dialogue_Roles.system,msg=msg))

    def think(self,msg : str):
        # DEBUG
        print(f'[Debug]:{self.role} thought: {msg}')

        self.conversational_memory.append(Dialgoue_line(role=self.role,msg=msg))

    def speak(self, message : str):
        self.broadcast(self.role, message)

    def react(self, dialogue_line : dict):
        pass

    def print_memory(self):
        print(self.conversational_memory)

class Conversation:
    def __init__(self):
        self._participants = []

    def add_participant(self, participant  : Conversation_Participant):
        if not isinstance(participant,Conversation_Participant):
            print(f'Given object is not a Conversation_Participant. Aborting add_participant routine ...')
            return

        participant.broadcast = self.broadcast_message
        self._participants.append(participant)

    def broadcast_message(self, role : str, msg : str):
        # DEBUG
        print(f'[Debug]: {role} said: {msg}')

        for participant in self._participants:
            participant : Conversation_Participant
            participant.conversational_memory.append(Dialgoue_line(role=role,msg=msg))












# ----------------------------------------------------
# Test driver code


def main():
    # Create a handler
    this_conversation = Conversation()

    # Create participants and add them to the handler
    participant1 = Conversation_Participant(role=Dialogue_Roles.agent)
    this_conversation.add_participant(participant1)

    participant2 = Conversation_Participant(role=Dialogue_Roles.agent)
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

# Expects output:
# assistant said: Hello from participant 1!
# assistant said: Hello from participant 2!
# assistant thought: I do not even want to say hello to that guy!
# Logs for Participant1:
# [{'role': 'assistant', 'content': 'Hello from participant 1!'}, {'role': 'assistant', 'content': 'Hello from participant 2!'}]
# Logs for Participant2:
# [{'role': 'assistant', 'content': 'Hello from participant 1!'}, {'role': 'assistant', 'content': 'Hello from participant 2!'}, {'role': 'assistant', 'content': 'I do not even want to say hello to that guy!'}]

if __name__ == "__main__":
    main()


# # Since rowdy_participant is itself an agent
# # this will trigger infinite recursion
# class Rowdy_participant(Conversation_Participant):
#     def react(self, dialogue_line : dict):
#         role = dialogue_line['role']
#         if role == Dialogue_Roles.agent:
#             self.speak('Actually, leave me alone! Let me talk to the user')
#
#         if role == Dialogue_Roles.user:
#             self.speak('Hello, how can I assist you today')
#
# participant3 = Rowdy_participant(Dialogue_Roles.agent)
# this_conversation.add_participant(participant3)
#
# participant1.speak('How are you :)')
#
# # Participants print their logs
# print("Logs for Participant1:")
# participant1.print_memory()
#
# print("Logs for Participant2:")
# participant2.print_memory()
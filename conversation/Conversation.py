from typing import List
from conversation.Conversation_Entry import Conversation_Entry
from conversation.Participant import Conversation_Participant
from conversation.Roles import Dialogue_Roles

# Conversation:
# -> Only Conversation Particpants can join a conversation
# -> The argument of speak is logged to "conversational_memory" of every particpant
# -> The arg of think is logged only to self
# -> For every new piece of dialgoue added to the conversational_memory "react" is triggered

# ----------------------------------------------------

# Those are the only three roles defined in the API. No other role can be introduced.



class Reactive_List(list):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback

    def append(self, item):
        super().append(item)
        if self.callback:
            self.callback(item)


class Conversation:
    def __init__(self):
        self._participants : List[Conversation_Participant] = []

    def add_participant(self, participant  : Conversation_Participant):
        if not isinstance(participant, Conversation_Participant):
            print(f'Given object is not a Conversation_Participant. Aborting add_participant routine ...')
            return

        participant.broadcast = self.broadcast_message
        self._participants.append(participant)

    def broadcast_message(self, role : str, msg : str):
        print(f'[Debug]: {role} said: {msg}')

        for participant in self._participants:
            participant._conversational_memory.append(Conversation_Entry(role=role, msg=msg))




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
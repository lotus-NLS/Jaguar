from s1_conversation.Conversation import Conversation
from s1_conversation.Participant import Conversation_Participant
from s1_conversation.Roles import Dialogue_Roles



def speak_and_think():
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
    speak_and_think()


# ----------------------------------------------------
# Test driver code


# Since rowdy_participant is itself an s2_agent
# # this will trigger infinite recursion
# class Rowdy_participant(Conversation_Participant):
#     def react(self, dialogue_line : dict):
#         role = dialogue_line['role']
#         if role == Dialogue_Roles.s2_agent:
#             self.speak('Actually, leave me alone! Let me talk to the user')
#
#         if role == Dialogue_Roles.user:
#             self.speak('Hello, how can I assist you today')
#
# participant3 = Rowdy_participant(Dialogue_Roles.s2_agent)
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
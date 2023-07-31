from conversation_definition import Conversation
from participant import Conversation_Participant,Roles


# Create a handler
this_conversation = Conversation()

# Create participants and add them to the handler
participant1 = Conversation_Participant(role=Roles.agent, broadcasts = [this_conversation.broadcast_message])
this_conversation.add_participant(participant1)

participant2 = Conversation_Participant(role=Roles.agent, broadcasts = [this_conversation.broadcast_message])
this_conversation.add_participant(participant2)

# Participants write messages
participant1.speak('Hello from participant 1!')
participant2.speak('Hello from participant 2!')

# Participants print their logs
print("Logs for Participant1:")
participant1.print_memory()

print("Logs for Participant2:")
participant2.print_memory()
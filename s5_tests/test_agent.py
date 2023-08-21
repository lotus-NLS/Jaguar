from s2_agent.Agent import Agent
from s1_conversation.Conversation import ConversationParticipant, Conversation, Dialogue_Roles

# -------------------------
# Test driver code

test_conversation = Conversation()
the_bot = Agent()
test_conversation.add_participant(the_bot)

the_user = ConversationParticipant(role=Dialogue_Roles.user)
test_conversation.add_participant(the_user)

other_user = ConversationParticipant(role=Dialogue_Roles.user)
test_conversation.add_participant(other_user)


while True:
    the_user.speak(input(''))

    # the_bot.print_memory()
    # other_user.print_memory()
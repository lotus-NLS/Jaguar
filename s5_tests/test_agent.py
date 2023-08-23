from s2_agent.Agent import Agent
from s1_conversation.Conversation import ConversationParticipant, Conversation, Dialogue_Roles

# -------------------------
# Test driver code


the_bot = Agent()
the_user = ConversationParticipant(role=Dialogue_Roles.user)
other_user = ConversationParticipant(role=Dialogue_Roles.user)

test_conversation = Conversation()

while True:
    the_user.speak(input(''))

    # the_bot.print_memory()
    # other_user.print_memory()
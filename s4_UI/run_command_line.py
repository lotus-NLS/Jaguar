from s3_equipped_agent.BasicAgent import BasicAgent
from s1_conversation.Conversation import Conversation_Participant,Conversation, Dialogue_Roles


test_conversation = Conversation()
the_bot = BasicAgent()
test_conversation.add_participant(the_bot)

the_user = Conversation_Participant(role=Dialogue_Roles.user)
test_conversation.add_participant(the_user)

other_user = Conversation_Participant(role=Dialogue_Roles.user)
test_conversation.add_participant(other_user)

while True:
    the_user.speak(input(''))

    # the_bot.print_memory()
    # other_user.print_memory()
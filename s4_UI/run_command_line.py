from s3_equipped_agent.BasicAgent import BasicAgent
from s1_conversation.Conversation import Conversation_Participant,Conversation_Entry,Conversation, Dialogue_Roles


test_conversation = Conversation()
the_bot = BasicAgent()
test_conversation.add_participant(the_bot)

the_user = Conversation_Participant(role=Dialogue_Roles.user)
test_conversation.add_participant(the_user)

other_user = Conversation_Participant(role=Dialogue_Roles.user)
test_conversation.add_participant(other_user)


# TODO: The processing of the messages occuring immediately after the message is spoken leads
# to the wrong ordering of messages for other s1_conversation participants
# Because "react" of the bot triggers its own speak which is processed before before the
# outer speak command of the user

# I think that it could be solved by making reactions into seperate threads but that will still
# involve a race condition.
# Additionally, I'm not sure if I want the processing to go on while the s1_conversation can continue
# This should be discussed.

while True:
    the_user.speak(input(''))

    # the_bot.print_memory()
    # other_user.print_memory()
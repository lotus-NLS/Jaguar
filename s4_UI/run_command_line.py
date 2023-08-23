from s3_equipped_agent.BasicAgent import BasicAgent
from s1_conversation.Conversation import ConversationParticipant,Conversation, Dialogue_Roles


the_bot = BasicAgent()
the_user = ConversationParticipant(role=Dialogue_Roles.user)
other_user = ConversationParticipant(role=Dialogue_Roles.user)

test_conversation = Conversation()

while True:
    the_user.speak(input(''))
    print('Current conversation memory of the bot')
    the_bot.print_memory()
    # other_user.print_memory()

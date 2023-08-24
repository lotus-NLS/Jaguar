import time
from s3_equipped_agent.BasicAgent import BasicAgent
from s1_conversation.Conversation import ConversationParticipant,Channel, Dialogue_Roles


the_conversation = Channel()
the_bot = BasicAgent()
the_user = ConversationParticipant(role=Dialogue_Roles.user)
other_user = ConversationParticipant(role=Dialogue_Roles.user)

the_conversation.join_participants([the_bot, the_user, other_user])


while True:
    the_user.speak(input(''))
    print('Current conversation memory of the bot')
    time.sleep(1)
    the_bot.print_memory()
    # other_user.print_memory()

import time
from s3_equipped_agent.BasicAgent import BasicAgent
from s1_conversation.Conversation import ConversationParticipant,Channel, DialogueRole,enter_into_conversation



the_bot = BasicAgent()
the_user = ConversationParticipant(role=DialogueRole.user)
other_user = ConversationParticipant(role=DialogueRole.user)

basic_channel = Channel()
enter_into_conversation(channel=basic_channel,participant_list=[the_bot,the_user,other_user])


while True:
    the_user.speak(input(''))
    time.sleep(1)
    print('Current conversation memory of the bot')
    the_bot.print_memory()
    print('Current conversation memory of other user')
    other_user.print_memory()
    # other_user.print_memory()

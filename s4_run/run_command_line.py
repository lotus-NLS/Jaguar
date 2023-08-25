import time
from s3_equipped_agent.BasicAgent import BasicAgent
from s1_conversation.Conversation import ConversationParticipant,Channel, DialogueRole


the_conversation = Channel()
the_bot = BasicAgent()
the_user = ConversationParticipant(role=DialogueRole.user)
other_user = ConversationParticipant(role=DialogueRole.user)
for participant in [the_bot,the_user,other_user]:
    the_conversation.add_participant(logger=participant.log_entry)


while True:
    the_user.speak(input(''))
    print('Current conversation memory of the bot')
    time.sleep(1)
    the_bot.print_memory()
    # other_user.print_memory()

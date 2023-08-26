import time
from s3_tool_agent.BasicAgent import BasicAgent
from s1_conversation.Conversation import ConversationParticipant,Channel, DialogueRole,enter_into_conversation

# TODO: Collect common functionalities of run_command_line and run_GUI together
# it would probably best to do this through a test module and elimitage s4_run altogether
# TODO: Should prompt the user to set the API key if it's not already set introduce set_api_key_if_needed()
# i.e. check for the key where you expect it then prompt if you can't find it.
# Don't have to check the functionality of the key there since that's done in the model and the
# key working is model dependent anyway.

the_bot = BasicAgent()
the_user = ConversationParticipant(role=DialogueRole.user())
# other_user = ConversationParticipant(role=DialogueRole.user)

basic_channel = Channel()
enter_into_conversation(channel=basic_channel,participant_list=[the_bot,the_user])

# pdf_file_path = '/home/aiproj/Downloads/sample.pdf'

while True:
    the_user.speak(input(''))
    time.sleep(1)
    print('[Debug]: Current conversation memory of the bot')
    the_bot.print_memory()
    # print('Current conversation memory of other user')
    # other_user.print_memory()
    # other_user.print_memory()

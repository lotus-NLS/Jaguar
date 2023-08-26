import time
from s1_run.ToolAgent import ToolAgent
from s4_conversation.Conversation import ConversationParticipant,Channel, DialogueRole,enter_into_conversation

# TODO: Collect common functionalities of run_command_line and run_GUI together
# it would probably best to do this through a dedicated RUN module that unifies command line and GUI
# TODO: Should prompt the user to set the API key if it's not already set introduce set_api_key_if_needed()
# i.e. check for the key where you expect it then prompt if you can't find it.
# Don't have to check the functionality of the key there since that's done in the model and the
# key working is model dependent anyway.

the_bot = ToolAgent()
the_user = ConversationParticipant(role=DialogueRole.user())
# other_user = ConversationParticipant(role=DialogueRole.user)

basic_channel = Channel()
enter_into_conversation(channel=basic_channel,participant_list=[the_bot,the_user])

# pdf_file_path = '/home/aiproj/Downloads/sample.pdf'

# TODO: The agent can introduce itself. Basically it's its own instruction manual.
# This also should be general to all run applications
# the_user.speak('[Manual inquiry for user]: Who are you and what can you do?')

while True:
    the_user.speak(input(''))
    time.sleep(1)
    print('[Debug]: Current conversation memory of the bot')
    the_bot.print_memory()
    # print('Current conversation memory of other user')
    # other_user.print_memory()
    # other_user.print_memory()

import threading
import time

from Actions import Actions
import openai
from tools.Toolbox import Toolbox, Tool
import os
from conversation.conversation import Conversation_Participant, Dialogue_Roles
from conversation.conversation import  Conversation
import json

# ---------------------------------------------------------

class Models:
    gpt_35_16k = 'gpt-3.5-turbo-16k'
    gpt_35_4k = 'gpt-3.5-turbo'
    gpt_40_32k = 'gpt-4-32k-0613'
    gpt_40_8k = 'gpt-4-0613'




class Agent(Conversation_Participant):
    def __init__(self,api_key : str = '', model_type: str = Models.gpt_35_16k):
        # Set model
        super().__init__(Dialogue_Roles.agent)
        self.model_type = model_type
        self.api_key = api_key if not api_key == '' else self.get_api_key()

        # Set initial prompt
        with open('../protocol/prompt') as prompt_file:
            initial_prompt = prompt_file.read()
        self.register_system_message(msg=initial_prompt)

        # Set tools
        self.tool_list = [Toolbox.SAY(), Toolbox.WRITE(), Toolbox.READ()]
        self.tool_instructions = [tool.get_usage_instructions() for tool in self.tool_list]
        self.register_for_tool_feedback()

    # ---------------------------------------------------
    # Setup

    def register_for_tool_feedback(self):
        for tool in self.tool_list:
            tool.external_log = self.register_system_message

    # TODO: Must Confirm that the API key works after getting it
    @staticmethod
    def get_api_key() -> str:
        try:
            key = os.environ.get('openai_key')
            return key
        except:
            print('Failed to retrieve api key. Check /etc/environment for entry \’openai_key\’')
            exit(code=1)

    # ---------------------------------------------------
    # Callback

    def react(self, dialogue_line : dict):
        if dialogue_line['role'] == Dialogue_Roles.user:
            threading.Thread(target=self.process_user_request).start()

    # ---------------------------------------------------
    # Other

    def get_next_actions(self):
        return openai.ChatCompletion.create(
            model=Models.gpt_35_16k,
            messages=self.conversational_memory,
            functions=self.tool_instructions,
            function_call='auto')


    def use_tool(self, instructions):
        tool_name = instructions['name']
        tool_args_dict = json.loads(instructions['arguments'])

        tool_dict : dict[str,Tool] = {tool.name : tool for tool in self.tool_list}

        if tool_name in tool_dict:
            tool_dict[tool_name].handle_call(args_dict=tool_args_dict)


    def process_user_request(self):
        try:
            print("[Debug] Creating completion request.")

            openai.api_key = self.api_key

            # TODO: Ideally i would like to know more exactly what can happen here
            # I think that in particular it can happen that there is no message and just a function call
            actions = Actions(self.get_next_actions())
            print("[Debug] Received response from the model.")

            text_content = actions.get_text_content()
            tool_instructions = actions.get_function_call()

            if not text_content is None:
                self.speak(message=text_content)

            if not tool_instructions is None:
                self.use_tool(instructions=tool_instructions)

        except Exception as e:
            print(f'[Error] Unable to get response from GPT-3.5. {str(e)}\n')


# -------------------------
# Test driver code

test_conversation = Conversation()
the_bot = Agent()
test_conversation.add_participant(the_bot)

the_user = Conversation_Participant(role=Dialogue_Roles.user)
test_conversation.add_participant(the_user)

other_user = Conversation_Participant(role=Dialogue_Roles.user)
test_conversation.add_participant(other_user)

# TODO: The processing of the messages occuring immediately after the message is spoken leads
# to the wrong ordering of messages for other conversation participants
# Because "react" of the bot triggers its own speak which is processed before before the
# outer speak command of the user

# I think that it could be solved by making reactions into seperate threads but that will still
# involve a race condition.
# Additionally, I'm not sure if I want the processing to go on while the conversation can continue
# This should be discussed.

while True:
    the_user.speak(input(''))

    # the_bot.print_memory()
    # other_user.print_memory()
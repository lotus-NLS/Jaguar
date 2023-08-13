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
    def __init__(self, model_type: str = Models.gpt_35_16k):
        # Set model
        super().__init__(Dialogue_Roles.agent)
        self.model_type = model_type

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

    # ---------------------------------------------------
    # Callback

    def react(self, dialogue_line : dict):
        if dialogue_line['role'] == Dialogue_Roles.user:
            self.process_user_request()

    # ---------------------------------------------------
    # Other

    def handle_function_call(self, funct_call):
        tool_name = funct_call['name']
        tool_args_dict = json.loads(funct_call['arguments'])

        tool_dict : dict[str,Tool] = {tool.name : tool for tool in self.tool_list}

        if tool_name in tool_dict:
            tool_dict[tool_name].handle_call(args_dict=tool_args_dict)


    def process_user_request(self):
        try:
            print("[Debug] Creating completion request.")

            response = openai.ChatCompletion.create(
                model=Models.gpt_35_16k,
                messages=self.conversational_memory,
                functions=self.tool_instructions,
                function_call='auto'
            )

            # TODO: Ideally i would like to know more exactly what can happen here
            # I think that in particular it can happen that there is no message and just a function call
            best_response = response['choices'][0]['message']
            agent_msg = best_response['content']
            funct_call = best_response['function_call']

            print("[Debug] Received response from the model.")

            self.handle_function_call(funct_call)
            self.speak(agent_msg)

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

while True:
    the_user.speak(input(''))
    the_bot.print_memory()
    other_user.print_memory()





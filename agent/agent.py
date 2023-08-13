import openai
from tools.Toolbox import Toolbox
import os
from conversation.conversation import Conversation_Participant

# ---------------------------------------------------------

class Models:
    gpt_35_16k = 'gpt-3.5-turbo-16k'
    gpt_35_4k = 'gpt-3.5-turbo'
    gpt_40_32k = 'gpt-4-32k-0613'
    gpt_40_8k = 'gpt-4-0613'


class Roles:
    user = 'user'
    agent = 'assistant'
    system = 'system'


class Agent(Conversation_Participant):
    def __init__(self, model_type: str = Models.gpt_35_16k,):
        super().__init__(Roles.agent)

        # TODO: This is deprecated and has to be removed after conversation update
        self.last_response = ''


        self.model_type = model_type

        with open('../protocol/prompt') as prompt_file:
            initial_prompt = prompt_file.read()

        self.register_system_message(msg=initial_prompt)

        self.tool_list = [Toolbox.SAY(), Toolbox.WRITE(), Toolbox.READ()]
        self.register_for_tool_feedback()

    def register_for_tool_feedback(self):
        for tool in self.tool_list:
            tool.external_log = self.register_system_message

    def execute_specified_functions(self, msg):
        print(f"[Debug] Processing GPT message: '{msg}'")
        processed_msg = ""
        current_tool = None
        tool_found = False  # Boolean variable to indicate if a starting keyword was found

        for char in msg:
            processed_msg += char
            if not tool_found:  # Only look for a new tool if one hasn't been found yet
                for tool in self.tool_list:
                    if tool.get_start_keyword() in processed_msg:
                        current_tool = tool  # Save the current tool info
                        tool_found = True  # Indicate that a tool was found
                        break  # Once a tool is found, stop looking for other tools

            else:
                if current_tool.get_end_keyword() in processed_msg:
                    arg_str = extract_between_keywords(processed_msg, current_tool.get_start_keyword(),
                                                       current_tool.get_end_keyword())
                    print(f'[Debug] Found ending keyword')
                    print(f'[Debug] Arg_str:{arg_str}')

                    result = current_tool.handle_call(arg_str)
                    print(f'[Debug] Called function with result: {result}')  # Display the result

                    processed_msg = ""  # reset the processed_msg
                    tool_found = False  # Reset tool_found to look for a new tool


    def handle_user_msg(self, msg):
        self.add_user_log(msg)

        try:
            agent_msg = ""
            print("[Debug] Creating completion request.")
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self._conversation_history,
                stream=True
            )

            for chunk in response:
                if chunk['choices'][0]['delta']:
                    to_append = chunk['choices'][0]['delta']['content']  # extract the message
                else:
                    to_append = '\n'
                agent_msg += to_append  # append the chunk to the message
            print("[Debug] Received response from the model.")

            self.execute_specified_functions(agent_msg)
            self.add_agent_log(agent_msg)
            self.last_response = agent_msg

        except Exception as e:
            print(f'[Error] Unable to get response from GPT-3.5. {str(e)}\n')

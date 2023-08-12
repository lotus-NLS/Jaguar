import openai
from tools.Toolbox import Toolbox
from tools.Toolbox import extract_between_keywords

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


class Agent:
    def __init__(self, model_type: str = Models.gpt_35_16k):
        def set_initial_prompt():
            self.initial_prompt += "You are a software development agent based on a large langauge model embedded in the Lotus project " \
                                   "which is a framework for enabling large language models to do software development. " \
                                   "The following functions are available to use through simple text instructions:"
            for tool in self.tool_list:
                self.initial_prompt+=f'{tool.get_tool_info()}'

            self.add_system_log(self.initial_prompt)


        self.last_response = ''
        self.initial_prompt = ''
        self.model_type = model_type
        self.conversation_history = []

        self.tool_list = Toolbox.tool_list
        set_initial_prompt()

    def add_system_log(self,this_msg):
        self.conversation_history.append({"role": Roles.user, "content": this_msg})

    def add_user_log(self,this_msg):
        self.conversation_history.append({"role": Roles.user, "content": this_msg})

    def add_agent_log(self,this_msg):
        self.conversation_history.append({"role": Roles.agent, "content": this_msg})

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
                messages=self.conversation_history,
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




# if __name__ == "__main__":
#     agent = Agent()
#
#     write_instruction = 'WRITE|START_path|/home/daniel/pyWriter/new_test.txt|END_path*START_content|helloworld|END_content*|WRITE'
#     read_instruction = 'READ|START_path|/home/daniel/pyWriter/new_test.txt|END_path*|READ'
#     totalinstr = write_instruction+read_instruction
#
#     agent.execute_specified_functions(totalinstr)

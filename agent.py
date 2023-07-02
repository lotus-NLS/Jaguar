import openai

from globals.method_lib import *
from globals.class_lib import *
from globals.tools import *

# ---------------------------------------------------------


class Agent:
    def __init__(self, model_type: str = Models.gpt_35_16k):
        def set_initial_prompt():
            toolbox_description = "You are a software development agent based on a large langauge model embedded in the Lotus project " \
                                  "which is a framework for enabling large language models to do software development" \
                                  "The following functions are available to use through simple text instructions:"
            for tool in self.toolbox:
                toolbox_description+=f'{tool.get_tool_info()}'
            self.initial_prompt = f'You have access to the following tools:{toolbox_description}'

        def create_agent_toolbox():
            return [Tools.read, Tools.write]

        self.initial_prompt = ''
        self.model_type = model_type
        self.conversation_history = []

        self.toolbox = create_agent_toolbox()
        set_initial_prompt()


    # def add_user_log(self,this_msg):
    #     self.conversation_history.append({"role": Roles.user, "content": this_msg})
    #
    # def add_agent_log(self,this_msg):
    #     self.conversation_history.append({"role": Roles.agent, "content": this_msg})
    #
    # def handle_new_user_msg(self, user_msg):
    #     self.add_user_log(user_msg)
    #     agent_msg = self.get_response(self.conversation_history)
    #     self.add_agent_log(agent_msg)

    # def get_response(self, msg):
    #     self.add_user_log(msg)
    #
    #     try:
    #         agent_msg = ""
    #         print("[Debug] Creating completion request.")
    #         response = openai.ChatCompletion.create(
    #             model="gpt-3.5-turbo",
    #             messages=self.conversation_history,
    #             stream=True
    #         )
    #
    #         for chunk in response:
    #             if chunk['choices'][0]['delta']:
    #                 to_append = chunk['choices'][0]['delta']['content']  # extract the message
    #             else:
    #                 to_append = '\n'
    #             agent_msg += to_append  # append the chunk to the message
    #         print("[Debug] Received response from the model.")
    #         return agent_msg
    #
    #     except Exception as e:
    #         print(f'[Error] Unable to get response from GPT-3.5. {str(e)}\n')


    def process_gpt_message(self, msg):
        print(f"[Debug] Processing GPT message: '{msg}'")
        processed_msg = ""
        current_tool = None
        tool_found = False  # Boolean variable to indicate if a starting keyword was found

        for char in msg:
            processed_msg += char
            if not tool_found:  # Only look for a new tool if one hasn't been found yet
                for tool in self.toolbox:
                    keyword = tool.get_start_keyword()
                    if keyword in processed_msg:
                        current_tool = tool  # Save the current tool info
                        tool_found = True  # Indicate that a tool was found
                        break  # Once a tool is found, stop looking for other tools
            else:
                end_keyword = current_tool.get_end_keyword()  # use method to get end_keyword
                if end_keyword in processed_msg:
                    arg_str = extract_between_keywords(processed_msg, current_tool.get_start_keyword(), end_keyword)

                    print(f'[Debug] Found ending keyword')
                    print(f'[Debug] Arg_str:{arg_str}')
                    current_tool.handle_call(arg_str)

                    # result = current_tool.function(*args)  # use function attribute directly
                    # print(f'[Debug] Called function with result: {result}')  # Display the result
                    # processed_msg = ""  # reset the processed_msg
                    # tool_found = False  # Reset tool_found to look for a new tool

        if not tool_found:  # If no tool was found in the last processed message
            print("[Debug] No keyword found in message")
        return None

if __name__ == "__main__":
    agent = Agent()

    # Print out the initial prompt to see what tools are available and how to use them
    print(agent.initial_prompt)

    # Construct a command to read a file
    read_message = "START_READ|--START_PATH|example.txt|--END_PATH|/READ"
    agent.process_gpt_message(read_message)

    # Construct a command to write to a file
    write_message = "START_WRITE|--START_PATH|example2.txt|--END_PATH|--START_CONTENT|Hello, World!--END_CONTENT|/WRITE"
    agent.process_gpt_message(write_message)

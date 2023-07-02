import openai
import re

from globals.method_lib import *
from globals.class_lib import *


class Agent:
    def __init__(self, model_type: str = Models.gpt_35_16k):
        def set_initial_prompt():
            toolbox_description = ""
            for tool_name, tool_info in self.toolbox.items():
                args_description = ""
                for arg in tool_info["args"]:
                    args_description += f"\n--{arg.upper()}\n[arg_value]\n--END_{arg.upper()}"
                usage_instruction = f"{tool_info['keyword']}{args_description}\n\\{tool_info['keyword']}"
                toolbox_description += f"\n - {tool_name}: {tool_info['description']} To use it, follow this format:\n{usage_instruction}"
            self.initial_prompt = f'You have access to the following tools:{toolbox_description}'

        self.initial_prompt = ''
        self.model_type = model_type
        self.conversation_history = []
        self.toolbox = self.create_toolbox()

        set_initial_prompt()

    @staticmethod
    def create_toolbox():
        toolbox = {
            "read_file": {
                "function": Tools.read_file,
                "keyword": "READ",
                "args": ["path"],
                "description": "The 'READ' tool allows you to read the contents of a file."
            },
            "write_file": {
                "function": Tools.write_file,
                "keyword": "WRITE",
                "args": ["path", "content"],
                "description": "The 'WRITE' tool allows you to write content to a file."
            }
        }
        return toolbox

    @staticmethod
    def get_tool_args(args_specfication):
        args = {}
        for line in args_specfication.splitlines():  # Split by new lines
            if line.startswith('--') and line.endswith(']'):  # If line is argument line
                arg_name, arg_val = line[2:].split('[', 1)  # Split by first '[' after '--'
                arg_val = arg_val.rsplit(']', 1)[0]  # Split by last ']' and get first part
                args[arg_name.strip()] = arg_val.strip()  # Trim and save the argument

        return args.values()  # Return only the values in the order they were in the message

    def add_to_conversation(self, role, msg):
        self.conversation_history.append({"role": role, "content": msg})


    def handle_new_user_msg(self,msg):
        self.add_to_conversation(Roles.user, msg)
        agent_msg = self.get_response(self.conversation_history)
        self.add_to_conversation(Roles.agent,agent_msg)
        self.process_gpt_message(agent_msg)

    def get_response(self, msg):
        try:
            agent_msg = ""

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
            return agent_msg

        except Exception as e:
            print(f'Error: Unable to get response from GPT-3.5. {str(e)}\n')

    def process_gpt_message(self, msg):
        print(f"Processing GPT message: '{msg}'")
        processed_msg = ""
        current_tool=''

        for char in msg:
            processed_msg += char
            for tool_name, tool_info in self.toolbox.items():
                keyword = tool_info["keyword"]
                if keyword in processed_msg:
                    current_tool = keyword

                end_keyword = "\\" + current_tool
                if end_keyword in processed_msg:
                    arg_str = extract_between_keywords(processed_msg, keyword, end_keyword)
                    args = self.get_tool_args(arg_str)
                    result = tool_info["function"](*args)
                    print(f'Called function with result: {result}')  # Display the result
                    processed_msg = ""  # reset the processed_msg

        print("No keyword found in message")
        return None



agent = Agent()

print(agent.initial_prompt)

# Test the process_gpt_message method with a read command
# message = "I want to READ a file. --path=/home/user/documents/file.txt \\path \\READ"
# print(agent.process_gpt_message(message))

# Test the process_gpt_message method with a write command
# message = "I would like to WRITE to a file. --path=/home/user/documents/file.txt --content=Hello, World! \\path \\content \\WRITE"
# print(agent.process_gpt_message(message))

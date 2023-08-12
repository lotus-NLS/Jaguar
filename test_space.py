import openai
import json
import os

from openai.openai_object import OpenAIObject
from tools.Toolbox import Toolbox

# from agents.agent import Models


class Models:
    gpt_35_16k = 'gpt-3.5-turbo-16k'
    gpt_35_4k = 'gpt-3.5-turbo'
    gpt_40_32k = 'gpt-4-32k-0613'
    gpt_40_8k = 'gpt-4-0613'

# Setup agent
inital_prompt = f'Can you please say some friendly words to welcome our guests?'

# Set API key
# openai.api_key = os.environ.get('openai_key')

openai.api_key = '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'

# -------------------------------------------------

# Define function

# TODO: The JSON that describes the function to the agent
# is something that should be generated on the fly

def run_conversation():
    messages = [{"role": "user", "content": f"{inital_prompt}"}]

    say_hi = Toolbox.Say_hi()
    say_hi_doc = say_hi.get_tool_info()

    functions = [say_hi_doc]

    response = openai.ChatCompletion.create(
        model=Models.gpt_35_16k,
        messages=messages,
        functions=functions,
        function_call='auto'
    )

    best_response = response['choices'][0]['message']
    # Here: best_response['function_call'] contains details of function call  and content is none.
    # If no functions are specified the content will be the message string received from the agent.

    best_response : OpenAIObject

    if 'function_call' in best_response.keys():
        funct_call = best_response['function_call']
        # funct_name = funct_call['name']
        funct_args = json.loads(funct_call['arguments'])

        say_hi.handle_call(funct_args)

    print('done')


run_conversation()
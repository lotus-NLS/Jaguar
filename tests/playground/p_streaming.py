import openai
from src.l3_lotus_core import Entry, DialogueRole
from src.l2_lotus_agent import Action
from src.l2_lotus_agent import ActionOptions, FunctCallOption
from src.l2_lotus_agent import LLM



class OpenAI_ModelTypes:
    # The 0613 models support function calling. Earlier models do not.
    # (06.13.23 is the date of the API updates https://openai.com/blog/function-calling-and-other-api-updates)
    # 'gpt-4' or 'gpt-3.5-turbo' point to the newest version of either model available on the API

    gpt_35_4k = 'gpt-3.5-turbo-0613'
    gpt_35_16k = 'gpt-3.5-turbo-16k-0613'
    gpt_40_8k = 'gpt-4-0613'
    gpt_40_32k = 'gpt-4-32k-0613'

    @staticmethod
    def get_test_model():
        return OpenAI_ModelTypes.gpt_35_4k



# The cl100k_base encoder is the encoder used for 0314 and 0613 versions of 3.5 and 4
# (https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
class OpenAIModel(LLM):
    def __init__(self, model_type : str):
        super().__init__(model_type=model_type)


    def get_action(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
        file_path = "/home/daniel/openai_key.txt"
        with open(file_path, "r") as file:
            openai.api_key = file.read().strip()

        args_dict = {
            'model': self.model_type,
            'messages': entries,
            'temperature': action_options.temperature
        }

        if action_options.get_funct_call_allowed():
            args_dict['functions'] = tool_docs
            args_dict['function_call'] = action_options.funct_call_options.get_openai_syntax()

        if not action_options.max_tokens is None:
            args_dict['max_tokens'] = action_options.max_tokens

        print(f'Creating completion request')
        openai_response = openai.ChatCompletion.create(**args_dict,stream=True)

        for chunk in openai_response:
            chunk_message = chunk['choices'][0]['delta']
            print(f'Received message: {chunk_message}')

        print(f"[Debug]: Received response from the model.")


        return Action(openai_response)




# ----------------------------------------------------------------------------

basic_entry = Entry(role=DialogueRole.system_role(),msg='Please greet our esteemed guests from Finland in both Finnish and in English')
this_instance = OpenAIModel(model_type=OpenAI_ModelTypes.gpt_35_4k)

action = this_instance.get_action(entries=[basic_entry],
           tool_docs=[],
           action_options=ActionOptions(funct_call_options=FunctCallOption.make_no_call_option())
          )
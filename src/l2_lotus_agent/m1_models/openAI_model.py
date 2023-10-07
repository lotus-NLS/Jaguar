import openai
import tiktoken
from typing import Optional
from src.l3_lotus_core import get_setting, Credentials, Entry

from src.l2_lotus_agent.m1_models.model_class import LLM
from src.l2_lotus_agent.m1_models.action import Action, ActionOptions


# ---------------------------------------------------------

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
        super().__init__(model_type=model_type, encoding = tiktoken.get_encoding('cl100k_base'))
        self.tokens_at_last_response : Optional[int] = None


    def get_action(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
        openai.api_key = get_setting(label=Credentials.openai_apikey_label)

        args_dict = {
            'model': self._model_type,
            'messages': entries,
            'temperature': action_options.temperature
        }

        if action_options.funct_call_options.call_allowed:
            args_dict['functions'] = tool_docs
            args_dict['function_call'] = action_options.funct_call_options.get_openai_syntax()

        if not action_options.max_tokens is None:
            args_dict['max_tokens'] = action_options.max_tokens

        self.log_request(entries=entries, tool_docs=tool_docs)
        openai_response = openai.ChatCompletion.create(**args_dict)
        self.log_response()


        return Action(openai_response)


    def log_request(self, entries : list[Entry], tool_docs : list[dict]):
        # Alternatively exact tokens used up to and including response can be obtained via the response object
        # openai_response['usage']['prompt_tokens']
        
        input_tokens_used = self.tokenizer.get_context_tokens(entries=entries, funct_docs=tool_docs)
        print(f'[Debug]: Creating completion request; Currently at {input_tokens_used} input tokens used')
        # print(f'[Debug]: Current conversation memory of {self._model_type}: [...] {str(entries)[-500:]}')


    @staticmethod
    def log_response():
        print(f"[Debug]: Received response from the model.")



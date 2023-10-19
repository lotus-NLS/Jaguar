import openai
import tiktoken
from openai_function_tokens import estimate_tokens
# from typing import Optional
from src.l3_lotus_core import get_setting, Entry, CredentialSettings
from src.l2_lotus_agent.m2_action import Action, ActionOptions

from .llm import LLM


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


    def get_action(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
        openai.api_key = get_setting(label=CredentialSettings.openai_apikey_label)

        args_dict = {
            'model': self._model_type,
            'messages': entries,
            'temperature': action_options.temperature
        }

        func_call_options = action_options.funct_call_options
        if func_call_options.call_allowed:
            args_dict['functions'] = tool_docs
            args_dict['function_call'] = func_call_options.get_openai_syntax()

        if not action_options.max_tokens is None:
            args_dict['max_tokens'] = action_options.max_tokens

        print(f'[Debug]: Creating completion request')
        openai_response = openai.ChatCompletion.create(**args_dict)
        input_tokens_used = openai_response['usage']['prompt_tokens']
        # counted_input_tokens = self.tokenizer.get_context_tokens(entries=entries,funct_docs = tool_docs)

        functions = tool_docs if func_call_options.call_allowed else None
        counted_input_tokens = estimate_tokens(messages=entries,
                                               functions=functions,
                                               function_call=action_options.funct_call_options.get_openai_syntax())
        print(f"[Debug]: Received response from the model; Currently at {input_tokens_used}; Estimated {counted_input_tokens}")

        return Action(openai_response)


import math
import openai
from openai_function_tokens import estimate_tokens
from src.l3_lotus_core import get_setting, Entry, CredentialSettings

from .action import Action, ActionOptions
from .llm import LLM


# ---------------------------------------------------------

class ModelTypes_OpenAI:
    # The 0613 models support function calling. Earlier models do not.
    # (06.13.23 is the date of the API updates https://openai.com/blog/function-calling-and-other-api-updates)
    # 'gpt-4' or 'gpt-3.5-turbo' point to the newest version of either model available on the API

    gpt_35_4k = 'gpt-3.5-turbo-0613'
    gpt_35_16k = 'gpt-3.5-turbo-16k-0613'
    gpt_40_8k = 'gpt-4-0613'
    gpt_40_32k = 'gpt-4-32k-0613'

    @staticmethod
    def get_test_model():
        return ModelTypes_OpenAI.gpt_35_4k


class OpenAIModel(LLM):
    def __init__(self, model_type : str):
        super().__init__(model_type=model_type)


    def get_action(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> Action:
        openai.api_key = get_setting(label=CredentialSettings.openai_apikey_label)

        args_dict = {
            'model': self.model_type,
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


        exact_prompt_tokens = openai_response['usage']['prompt_tokens']
        exact_compl_tokens = openai_response['usage']['completion_tokens']

        functions = tool_docs if func_call_options.call_allowed else None
        counted_input_tokens = estimate_tokens(messages=entries,
                                               functions=functions,
                                               function_call=action_options.funct_call_options.get_openai_syntax())

        cent_costs = self._get_request_cost_cents(num_input_tokens=exact_prompt_tokens,num_output_tokens=exact_compl_tokens)
        print(f"[Debug]: Received response from the model; Currently at {exact_prompt_tokens}; Estimated {counted_input_tokens}"
              f";Estimated costs in cents: {cent_costs} ")

        return Action(openai_response)


    def _get_request_cost_cents(self, num_input_tokens : int, num_output_tokens : int):
        num_input_kt = math.ceil(num_input_tokens/1000.)
        num_output_kt = math.ceil(num_output_tokens/1000.)

        cost_input_kt = self._get_centcost_per_kt(is_input=True)
        cost_output_kt = self._get_centcost_per_kt(is_input=False)

        return num_input_kt*cost_input_kt+num_output_kt*cost_output_kt


    def _get_centcost_per_kt(self, is_input: bool) -> float:
        if self.model_type == ModelTypes_OpenAI.gpt_40_8k:
            return 3 if is_input else 6
        elif self.model_type == ModelTypes_OpenAI.gpt_40_32k:
            return 6 if is_input else 12
        elif self.model_type == ModelTypes_OpenAI.gpt_35_4k:
            return 0.15 if is_input else 0.2
        elif self.model_type == ModelTypes_OpenAI.gpt_35_16k:
            return 0.3 if is_input else 0.4
        else:
            return 0
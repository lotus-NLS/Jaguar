import math
import openai
from openai_function_tokens import estimate_tokens
from lotusEngine.l3_lotus_core import get_setting, Entry, CredentialSettings

from .actionstream import ActionStream
from .options import ActionOptions
from .llm import LLM

# ---------------------------------------------------------


class OpenAIModel(LLM):
    def __init__(self, model_type : str):
        super().__init__(model_type=model_type)


    def get_action_stream(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> ActionStream:
        openai.api_key = get_setting(label=CredentialSettings.openai_apikey_label)

        args_dict = {
            'model': self.model_type,
            'messages': entries,
            'temperature': action_options.temperature,
            'stream' : True
        }

        func_call_options = action_options.funct_call_options
        if func_call_options.call_allowed:
            args_dict['functions'] = tool_docs
            args_dict['function_call'] = func_call_options.get_openai_syntax()

        if not action_options.max_tokens is None:
            args_dict['max_tokens'] = action_options.max_tokens


        self._log_request()
        openai_response = openai.ChatCompletion.create(**args_dict)
        self._log_response(entries, tool_docs, action_options)

        return ActionStream(openai_response)

    # ---------------------------------------------------
    # Logging

    @staticmethod
    def _log_request():
        print(f'[Debug]: Creating completion request')


    # For non stream responses can also obtain exact token usage (see: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
    # exact_prompt_tokens = openai_response['usage']['prompt_tokens']
    # exact_compl_tokens = openai_response['usage']['completion_tokens']
    def _log_response(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions):
        functions = tool_docs if action_options.funct_call_options.call_allowed else None
        counted_input_tokens = estimate_tokens(messages=entries,
                                               functions=functions,
                                               function_call=action_options.funct_call_options.get_openai_syntax())

        cent_costs = self._get_request_cost_cents(num_input_tokens=counted_input_tokens, num_output_tokens=0)
        print(f"[Debug]: Received response from the model; Estimated {counted_input_tokens} input tokens for {cent_costs} cents cost on input")


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
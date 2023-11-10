import openai
import json
from typing import Optional
from pyutils import DevLogger
from api.classes.language import Entry
from engine.l3_singletons import CredentialSettings

from .actionstream import ActionStream
from .options import ActionOptions
from .llm import LLM

# ---------------------------------------------------------


class OpenAIModel(LLM):
    def __init__(self, model_type : str):
        super().__init__(model_type=model_type)

    def get_action_stream(self, entries: list[Entry], tool_docs: list[dict], action_options: ActionOptions) -> ActionStream:
        openai.api_key = CredentialSettings().get_openai_key()

        args_dict = {
            'model': self.model_type,
            'messages': entries,
            'temperature': action_options.temperature,
            'stream' : True
        }

        func_call_options = action_options.funct_call_options
        if func_call_options.call_allowed:

            args_dict['tools'] = tool_docs
            args_dict['tool_choice'] = func_call_options.get_openai_syntax()

        if not action_options.max_tokens is None:
            args_dict['max_tokens'] = action_options.max_tokens


        self._log_request()
        openai_response = openai.ChatCompletion.create(**args_dict)
        self._log_response()

        return ActionStream(openai_response)

    # ---------------------------------------------------
    # Logging

    @staticmethod
    def _log_request():
        print(f'[Debug]: Creating completion request')

    @staticmethod
    def _log_response():
        print(f"[Debug]: Received response from the model")

    # Accurate up to ~10%
    def get_tokens_estimate(self, entries: list[Entry], tool_docs : Optional[list[dict]] = None) -> Optional[int]:
        try:
            token_count = 0
            the_tools = [] if tool_docs is None else tool_docs
            for entry in entries:
                token_count += self.get_num_tokens(f'{entry}')
            for tool_docs in the_tools:
                token_count += json.dumps(tool_docs)
            return token_count
        except Exception as e:
            DevLogger.print_error(text=f'Failed to estimate token count: {e}')
            return None


class ModelTypes_OpenAI:
    # The 0613 models support function calling. Earlier models do not.
    # (06.13.23 is the date of the API updates https://openai.com/blog/function-calling-and-other-api-updates)
    # 'gpt-4' or 'gpt-3.5-turbo' point to the newest version of either model available on the API

    gpt_35_4k = 'gpt-3.5-turbo-0613'
    gpt_35_16k = 'gpt-3.5-turbo-1106'
    gpt_40_8k = 'gpt-4-0613'
    gpt_40_128k = 'gpt-4-1106-preview'

    @staticmethod
    def get_test_model():
        return ModelTypes_OpenAI.gpt_35_4k
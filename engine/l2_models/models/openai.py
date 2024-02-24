import openai
import logging
from typing import Optional
from api import Entry

from engine.l4_singletons import LotusSettings
from ..llm import LLM, Generation
from .. import GenerationOptions
from enum import Enum
# ---------------------------------------------------------


class OpenAIModel(LLM):
    def __init__(self, model_type : str):
        super().__init__(model_type=model_type)

    def get_generation(self, entries: list[Entry],
                       tool_docs: list[dict],
                       options: GenerationOptions) -> Generation:
        openai.api_key = LotusSettings().get_openai_apikey()

        args_dict = {
            'model': self.model_type,
            'messages': [entry.as_dict() for entry in entries],
            'temperature': options.temperature,
            'stream' : True
        }

        func_call_options = options.tool_options
        if func_call_options.call_allowed and tool_docs:
            args_dict['tools'] = tool_docs
            args_dict['tool_choice'] = func_call_options.get_openai_syntax()

        if not options.max_tokens is None:
            args_dict['max_tokens'] = options.max_tokens


        self._log_request()
        openai_generator = openai.ChatCompletion.create(**args_dict)
        self._log_response(entries=entries,tool_docs=tool_docs)

        return Generation(generator=openai_generator)

    # ---------------------------------------------------
    # Logging

    def _log_request(self):
        self.log(f'Creating completion request')

    def _log_response(self,entries: list[Entry], tool_docs : Optional[list[dict]] = None):
        tokens_estimate = self.tokenizer.get_tokens_estimate(entries=entries,tool_docs=tool_docs)
        self.log(f"Received response from the model; Currently at ~ {tokens_estimate} tokens")


class ModelsOpenAI(Enum):
    # The 0613 l2_models support function calling. Earlier models do not.
    # (06.13.23 is the date of the API updates https://openai.com/blog/function-calling-and-other-api-updates)
    # 'gpt-4' or 'gpt-3.5-turbo' point to the newest version of either model available on the API

    gpt_40_std = 'gpt-4'
    gpt_35_std = 'gpt-3.5-turbo'
    gpt_35_16k = 'gpt-3.5-turbo-1106'
    gpt_40_8k = 'gpt-4-0613'
    gpt_40_128k = 'gpt-4-1106-preview'
    gpt_40_vision = 'gpt-4-vision-preview'

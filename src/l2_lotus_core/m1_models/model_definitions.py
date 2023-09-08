import openai

from src.l2_lotus_core.m1_models.model_class import LLM, FunctionCallModes
from src.l2_lotus_core.m1_models.actioncontent import ActionContent, ActionOptions
from src.l2_lotus_core.m1_models.model_class import Context

from src.l2_lotus_core.m1_settings.settings_manager import get_openai_apikey
# ---------------------------------------------------------

class OpenAI_ModelTypes:
    # The 0613 m1_models (06.13.23, the date of the API updates (https://openai.com/blog/function-calling-and-other-api-updates)
    # support function calling
    # But gpt-4 or gpt-3.5-turbo will always point to the newest version anyway

    gpt_35_4k = 'gpt-3.5-turbo-0613'
    gpt_35_16k = 'gpt-3.5-turbo-16k-0613'
    gpt_40_8k = 'gpt-4-0613'
    gpt_40_32k = 'gpt-4-32k-0613'

    @staticmethod
    def get_test_model():
        return OpenAI_ModelTypes.gpt_35_4k


class OpenAIModel(LLM):
    def __init__(self, model_type : str):
        super().__init__(name=model_type)
        self._model_type = model_type

    @classmethod
    def make_gpt_35_4k(cls):
        return cls(model_type=OpenAI_ModelTypes.gpt_35_4k)

    @classmethod
    def make_gpt_35_16k(cls):
        return cls(model_type=OpenAI_ModelTypes.gpt_35_16k)

    @classmethod
    def make_gpt_40_8k(cls):
        return cls(model_type=OpenAI_ModelTypes.gpt_40_8k)

    @classmethod
    def make_gpt_40_32k(cls):
        return cls(model_type=OpenAI_ModelTypes.gpt_40_32k)

    def get_next_action(self, context : Context, action_options : ActionOptions) -> ActionContent:
        args_dict = {
            'model': self._model_type,
            'messages': context.msg_history,
            'temperature': action_options.temperature
        }

        if not context.tool_docs == 0:
            args_dict['functions'] = context.tool_docs
            args_dict['function_call'] = FunctionCallModes.auto if action_options.is_allowed_functioncall else FunctionCallModes.none

        if not action_options.max_tokens is None:
            args_dict['max_tokens'] = action_options.max_tokens

        openai.api_key = get_openai_apikey()
        openai_response = openai.ChatCompletion.create(**args_dict)

        # Action is promised a dict, so a dict must be delivered in any case
        if not isinstance(openai_response, dict):
            print('[Debug]: OpenAI response is not of dictionary type. Defaulting to empty response')
            openai_response = {}

        return ActionContent(openai_response)

import openai
import tiktoken

from src.l2_lotus_core.m3_settings import get_setting, Credentials

from src.l2_lotus_core.m1_models.model_class import LLM, FunctionCallModes
from src.l2_lotus_core.m1_models.action import Action, ActionOptions
from src.l2_lotus_core.m1_models.model_class import Context


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
        encoder_type = tiktoken.get_encoding('cl100k_base')
        self.encoder = encoder_type.encode
        self.decoder = encoder_type.decode



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


    def get_next_action(self, context : Context, action_options : ActionOptions) -> Action:
        args_dict = {
            'model': self._model_type,
            'messages': context.msg_history,
            'temperature': action_options.temperature
        }

        if not context.tool_docs is None and action_options.is_allowed_functioncall:
            args_dict['functions'] = context.tool_docs
            args_dict['function_call'] = FunctionCallModes.auto

        if not action_options.max_tokens is None:
            args_dict['max_tokens'] = action_options.max_tokens

        openai.api_key = get_setting(label=Credentials.openai_apikey_label)
        openai_response = openai.ChatCompletion.create(**args_dict)

        # Action is promised a dict, so a dict must be delivered in any case
        if not isinstance(openai_response, dict):
            raise TypeError(f'[Error]: OpenAI response is not of dictionary form')

        total_tokens_openai = openai_response['usage']['prompt_tokens']

        print(f'[Debug]: Before generation at {total_tokens_openai} tokens used; '
              f'Estimation: {self.get_total_token_count_estimation(context=context)}')

        return Action(openai_response)


    # The cl100k_base encoder is the encoder used for 0314 and 0613 versions of 3.5 and 4
    def get_token_count(self,the_str: str):
        return len(self.encoder(the_str))


    def get_limited_string(self, the_str : str, max_tokens : int):
        encoded_str = self.encoder(the_str)
        return self.decoder(encoded_str[:max_tokens])

    def get_total_token_count_estimation(self, context : Context):
        msg_history = context.msg_history
        tool_docs = context.tool_docs

        num_tokens = 0

        for msg in msg_history:
            num_tokens += self.get_token_count(the_str=msg.get_content())
            num_tokens += 3

        num_tokens += self.get_token_count(the_str=str(tool_docs))

        return num_tokens
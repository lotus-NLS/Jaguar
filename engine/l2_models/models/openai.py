import openai
from api import Entry

from engine.l4_singletons import LotusSettings
from ..llm import LLM, Generation, GenerationOptions, ModelType
# ---------------------------------------------------------


class OpenAIModelType(ModelType):
    GPT_4 = 'gpt-4'
    GPT_4_TURBO = 'gpt-4-1106-preview'
    GPT_4V = 'gpt-4-vision-preview'
    GPT_35 = 'gpt-3.5-turbo'


class OpenAIModel(LLM):
    def __init__(self, model_type : ModelType = OpenAIModelType.GPT_4):
        super().__init__(model=model_type)

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

        tool_options = options.tool_options
        if tool_options.call_allowed and tool_docs:
            args_dict['tools'] = tool_docs
            args_dict['tool_choice'] = tool_options.get_openai_syntax()

        if not options.max_tokens is None:
            args_dict['max_tokens'] = options.max_tokens


        self.log(f'Creating completion request')
        openai_generator = openai.ChatCompletion.create(**args_dict)
        token_count_estimate = self.tokenizer.get_tokens_estimate(entries=entries, tool_docs=tool_docs)
        self.log(f"Received response from the model; Currently at ~ {token_count_estimate} tokens")

        return Generation(generator=openai_generator)



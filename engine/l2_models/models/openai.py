from typing import Optional

import openai
from openai.openai_object import OpenAIObject

from ..generation.llm import LLM, ModelType
from ..generation.generation import Generation, Chunk, Options, GenerationContext
from engine.l3_applications.tool import ToolCall, CallMap
from engine.l4_singletons import Settings


# ---------------------------------------------------------

class OpenAIGeneration(Generation):
    def _get_next_chunk(self, chunk_data : OpenAIObject):
        return OpenAIChunk(data=chunk_data)


class OpenAIModelType(ModelType):
    GPT_4 = 'gpt-4-0125-preview'
    GPT_4_TURBO = 'gpt-4-turbo-preview'
    GPT_35 = 'gpt-3.5-turbo-0125'


class OpenAIChunk(Chunk):
    def __init__(self, data : OpenAIObject):
        super().__init__(data=data)
        self.best_response : Optional[dict] = data['choices'][0].get('delta')


    def get_text(self) -> Optional[str]:
        text_content = None
        if not self.best_response is None:
            text_content = self.best_response.get('content')
        return text_content


    def get_call_map(self) -> CallMap:
        tool_calls : Optional[dict] = self.best_response.get('tool_calls')
        if tool_calls is None:
            return CallMap()

        call_map : CallMap = CallMap()
        for openai_tool_call in tool_calls:
            index = openai_tool_call.get('index')
            call = call_map.get(index, ToolCall())
            new_data = openai_tool_call.get('function')
            new = ToolCall(name=new_data.get('name'), json_str=new_data.get('arguments'))

            call.update(partial_call=new)
            if not index in call_map:
                call_map[index] = call

        return call_map


class OpenAIModel(LLM):
    def __init__(self, model_type : ModelType = OpenAIModelType.GPT_4_TURBO):
        super().__init__(model_type=model_type)


    def get_generation(self, context : GenerationContext, options: Options) -> OpenAIGeneration:
        self.log(f'Creating generation request')
        openai_response = self.get_openai_response(context=context, options=options)
        self.log(f"Received generation response. Currently at {self.tokenizer.get_tokens(context=context)} tokens")

        return OpenAIGeneration(generator=openai_response)


    def get_openai_response(self, context : GenerationContext, options: Options):
        args_dict = {
            'model': self.model_type,
            'messages': [entry.as_dict() for entry in context.entries],
            'temperature': options.temp,
            'stream' : True
        }

        tool_options = options.tool_options
        if tool_options.call_allowed and context.docs:
            args_dict['tools'] = context.docs
            args_dict['tool_choice'] = tool_options.get_openai_syntax()

        if not options.max_tokens is None:
            args_dict['max_tokens'] = options.max_tokens

        openai.api_key = Settings().get_openai_apikey()
        openai_generator = openai.ChatCompletion.create(**args_dict)
        return openai_generator






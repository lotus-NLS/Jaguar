from typing import Optional

import openai
from openai.openai_object import OpenAIObject

from ..llm.llm import LLM, ModelType
from ..llm.generation import Generation, Chunk, Options, GenerationContext
from engine.l3_applications.tool import ToolCall
from engine.l4_singletons import Settings


# ---------------------------------------------------------


class OpenAIModelType(ModelType):
    GPT_4 = 'gpt-4'
    GPT_4_TURBO = 'gpt-4-1106-preview'
    GPT_4V = 'gpt-4-vision-preview'
    GPT_35 = 'gpt-3.5-turbo'


class OpenAIModel(LLM):
    def __init__(self, model_type : ModelType = OpenAIModelType.GPT_4):
        super().__init__(model=model_type)


    def get_generation(self, context : GenerationContext, options: Options) -> Generation:
        self.log(f'Creating generation request')
        openai_response = self.get_openai_response(context=context, options=options)
        self.log(f"Received generation response. Currently at {self.tokenizer.get_tokens(context=context)} tokens")

        return Generation(generator=openai_response)


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


class OpenAIGeneration(Generation):
    def get_next_chunk(self, data : OpenAIObject):
        return OpenAIChunk(data=data)



class OpenAIChunk(Chunk):
    def __init__(self, data : OpenAIObject):
        super().__init__(data=data)
        self.best_response : Optional[dict] = data['choices'][0].get('delta')


    def get_text(self) -> Optional[str]:
        text_content = None
        if not self.best_response is None:
            text_content = self.best_response.get('content')
        return text_content


    def get_call(self) -> Optional[ToolCall]:
        tool_calls : Optional[dict] = self.best_response.get('tool_calls')
        if tool_calls is None:
            return None

        tool_call = ToolCall()
        for openai_tool_call in tool_calls:
            index = openai_tool_call.get('index')
            funct_call = openai_tool_call.get('function')

            tool_call = ToolCall(name=funct_call.get('name'), json_str=funct_call.get('arguments'), index=index)
            tool_call.update(partial_call=tool_call)

        return tool_call
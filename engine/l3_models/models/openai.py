from __future__ import annotations
import openai
from typing import Optional
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta, ChoiceDeltaToolCall, ChatCompletionChunk
from openai import Stream

from api import Entry, APIType
from engine.l4_tools import ToolCall, CallMap
from engine.l5_singletons import Settings
from engine.l3_models.generation import LLM, ModelType
from engine.l3_models.generation import Generation, Chunk, Context, Options

# ---------------------------------------------------------

class OpenAIChunk(Chunk):
    def __init__(self, data : ChatCompletionChunk):
        super().__init__(data=data)
        self.data : ChatCompletionChunk = data
        self.best_choice : Optional[Choice] = data.choices[0]
        self.delta : ChoiceDelta = self.best_choice.delta

    def get_text(self) -> Optional[str]:
        text_content = None
        if not self.delta is None:
            text_content = self.delta.content
        return text_content


    def is_final(self) -> bool:
        finish_reason_present = not self.best_choice.finish_reason is None
        return finish_reason_present


    def get_call_map(self) -> CallMap:
        tool_calls : list[ChoiceDeltaToolCall] = self.delta.tool_calls
        if not tool_calls:
            return CallMap()

        call_map : CallMap = CallMap()
        for openai_tool_call in tool_calls:
            index = openai_tool_call.index
            call = call_map.get(index, ToolCall())

            new_data = openai_tool_call.function
            new = ToolCall(name=new_data.name, json_str=new_data.arguments)
            call.add(partial_call=new)
            if not index in call_map:
                call_map[index] = call

        return call_map


class OpenAIGeneration(Generation):
    def _get_next_chunk(self, chunk_data : ChatCompletionChunk) -> OpenAIChunk:
        return OpenAIChunk(data=chunk_data)



class OpenAIModelType(ModelType):
    @classmethod
    def get_gpt4(cls) -> OpenAIModelType:
        return cls(name='gpt-4', supports_vision=False)

    @classmethod
    def get_gpt4_turbo(cls) -> OpenAIModelType:
        return cls(name='gpt-4-turbo-preview', supports_vision=False)

    @classmethod
    def get_gpt4V(cls) -> OpenAIModelType:
        return cls(name='gpt-4-vision-preview', supports_vision=True)

    @classmethod
    def get_gpt35(cls) -> OpenAIModelType:
        return cls(name='gpt-3.5-turbo', supports_vision=False)


class OpenAIModel(LLM):
    def __init__(self, model_type : ModelType = OpenAIModelType.get_gpt4_turbo()):
        super().__init__(model_type=model_type)


    def get_generation(self, context : Context, options: Options) -> OpenAIGeneration:
        for entry in context.entries:
            if not isinstance(entry, Entry):
                raise TypeError(f'Entry {entry} is not of required type OpenAI but {type(entry)}')

        self.log(f'Creating generation request')
        openai_response = self.get_response(context=context, options=options)
        self.log(f"Received generation response. Currently at {self.tokenizer.get_tokens(context=context)} tokens")

        return OpenAIGeneration(generator=openai_response)


    def get_response(self, context : Context, options: Options) -> Stream[ChatCompletionChunk]:
        args_dict = {
            'model': self.model_type,
            'messages': [entry.as_dict(api_type=APIType.OPENAI, with_vision=self.supports_vision()) for entry in context.entries],
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
        openai_generator = openai.chat.completions.create(**args_dict)
        return openai_generator


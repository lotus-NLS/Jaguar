from __future__ import annotations

from openai import OpenAI
from func_timeout import func_timeout
from typing import Optional
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta, ChoiceDeltaToolCall, ChatCompletionChunk
from openai import Stream

from api import Entry, APIType
from engine.l2_models.generation import Generation, Chunk, Context, Options
from engine.l2_models.models.llm import LLM
from engine.l3_aos.tools import ToolCall

# ---------------------------------------------------------

class OpenAIModel(LLM):
    def __init__(self, name : str, api_key : str):
        super().__init__(name=name)
        self.openai_api_key : str = api_key
        self.client : OpenAI = OpenAI(api_key=api_key)

    @classmethod
    def default_model(cls, api_key : str) -> OpenAIModel:
        return cls(name='gpt-4o', api_key=api_key)

    def get_generation(self, context : Context, options: Options) -> Generation:
        for entry in context.entries:
            if not isinstance(entry, Entry):
                raise TypeError(f'Entry {entry} is not of required type OpenAI but {type(entry)}')

        self.log(f'Creating generation request')
        openai_response = self.get_response(context=context, options=options)
        self.log(f"Received generation response. Currently at {self.tokenizer.get_tokens(context=context)} tokens")

        return Generation(generator=openai_response, chunk_type=OpenAIChunk)

    def get_response(self, context : Context, options: Options) -> Stream[ChatCompletionChunk]:
        args_dict = {
            'model': self.get_name(),
            'messages': [entry.as_dict(api_type=APIType.OPENAI) for entry in context.entries],
            'temperature': options.temp,
            'stream' : True
        }

        tool_options = options.call_options
        if tool_options.call_allowed and context.docs:
            args_dict['tools'] = context.docs
            args_dict['tool_choice'] = tool_options.get_openai_syntax()

        if not options.max_tokens is None:
            args_dict['max_tokens'] = options.max_tokens

        def send_request():
            return self.client.chat.completions.create(**args_dict)
        openai_stream = func_timeout(func=send_request,timeout=10)
        return openai_stream


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


    def get_call_map(self) -> dict[int, ToolCall]:
        tool_calls : list[ChoiceDeltaToolCall] = self.delta.tool_calls
        if not tool_calls:
            return {}

        call_map : dict = {}
        for openai_tool_call in tool_calls:
            index = openai_tool_call.index
            call = call_map.get(index, ToolCall())

            new_data = openai_tool_call.function
            new = ToolCall(name=new_data.name, json_str=new_data.arguments)
            call.add(partial_call=new)
            if not index in call_map:
                call_map[index] = call

        return call_map


from __future__ import annotations

from typing import Optional

from openai import OpenAI
from openai import Stream
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta, ChoiceDeltaToolCall, ChatCompletionChunk

from engine.l2_models.context.ctx import Context
from engine.l2_models.context.entry import APIType, Entry
from engine.l2_models.generation import Generation, Chunk, InfOptions
from engine.l2_models.llm import LLM
from engine.l3_aos.tools import ToolCall


# ---------------------------------------------------------

class OpenAIModel(LLM):
    def make_client(self, api_key : Optional[str] = None):
        return OpenAI(api_key=api_key)

    @classmethod
    def default_model(cls, api_key : str) -> OpenAIModel:
        return cls(name='gpt-4o', api_key=api_key)

    def get_generation(self, context : Context, options: InfOptions) -> Generation:
        self.check_token_cap(context=context, token_cap=options.max_input_tokens)
        for entry in context.entries:
            if not isinstance(entry, Entry):
                raise TypeError(f'Entry {entry} is not of required type OpenAI but {type(entry)}')

        self.log(f'Creating generation request')
        openai_response = self.get_response(context=context, options=options)
        self.log(f"Received generation response. Currently at {self.tokenizer.count_context_tokens(context=context)} tokens")

        return Generation(generator=openai_response, chunk_type=OpenAIChunk)

    def get_response(self, context : Context, options: InfOptions) -> Stream[ChatCompletionChunk]:
        args_dict = {
            'model': self._name,
            'messages': [entry.as_dict(api_type=APIType.OPENAI) for entry in context.entries],
            'stream' : True,
            'timeout' : options.timeout
        }

        tool_options = options.call_options
        if tool_options.call_allowed and context.docs:
            args_dict['tools'] = context.docs
            args_dict['tool_choice'] = tool_options.get_openai_syntax()

        if not options.max_output_tokens is None:
            args_dict['max_tokens'] = options.max_output_tokens

        return self.client.chat.completions.create(**args_dict)


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
        openai_tool_calls : list[ChoiceDeltaToolCall] = self.delta.tool_calls
        if not openai_tool_calls:
            return {}

        calls : dict[int, ToolCall] = {}
        for c in openai_tool_calls:
            f = c.function

            name = f.name if not f.name is None else ''
            args = f.arguments if not f.arguments is None else ''
            if not isinstance(name, str):
                raise ValueError(f'Invalid tool call name: {f.name}, type = {type(f.name)}')
            if not isinstance(args, str):
                raise ValueError(f'Invalid tool call arguments: {f.arguments}, type = {type(f.arguments)}')
            calls[c.index] = ToolCall(name=name, json_str=args)

        return calls


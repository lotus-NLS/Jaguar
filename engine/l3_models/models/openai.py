from typing import Optional
import base64
from PIL.Image import Image as PILImage
import PIL.Image as Image
import openai
import io
from openai.types.chat import ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta, ChoiceDeltaToolCall
from openai import Stream


from api import Entry, Speaker
from api.language.entry import EntryData
from engine.l4_tools import ToolCall, CallMap
from engine.l5_singletons import Settings
from ..generation.llm import LLM, ModelType
from ..generation.generation import Generation, Chunk, Options, GenerationContext


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
            call.update(partial_call=new)
            if not index in call_map:
                call_map[index] = call

        return call_map


class OpenAIGeneration(Generation):
    def _get_next_chunk(self, chunk_data : ChatCompletionChunk) -> OpenAIChunk:
        return OpenAIChunk(data=chunk_data)



class OpenAIModelType(ModelType):
    GPT_4 = 'gpt-4-0125-preview'
    GPT_4_TURBO = 'gpt-4-turbo-preview'
    GPT_4V = 'gpt-4-vision-preview'
    GPT_35 = 'gpt-3.5-turbo-0125'



class OpenAIEntry(Entry):
    def add_msg(self, msg : str):
        content = self.get_content()
        if isinstance(content, str):
            new_content = content + msg
        else:
            old_text = content[0]['text']
            new_text = old_text + msg
            new_content = {'type': 'text', 'text': f"{new_text} {msg}"}
        self.data['content'] = new_content


    def create_data(self, speaker : Speaker, msg : str, image: Optional[PILImage] = None) -> EntryData:
        name = speaker.name if speaker.name else 'unnamed'
        role = speaker.role.value

        if msg and not image:
            content = msg
        else:
            base64_image = self.get_base64(image=image)
            text = {
                "type": "text",
                "text": f"{msg}"
            }
            image = {
                "type": "image_url",
                "image_url": {"url": f"data:image/JPEG;base64,{base64_image}"}
            }
            content =  [text, image]

        data = EntryData(role=role, name=name, content=content)
        return data


    @staticmethod
    def get_base64(image) -> Optional[str]:
        if image.mode in ('LA', 'RGBA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image = image.convert('RGB') if image.mode == 'RGBA' else image.convert('L').convert('RGB')
            background.paste(rgb_image, mask=image.split()[-1])
            image = background

        image.show()
        buffer = io.BytesIO()
        image.save(buffer, format=f'JPEG')
        img_bytes = buffer.getvalue()
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        return base64_image


class OpenAIModel(LLM):
    def __init__(self, model_type : ModelType = OpenAIModelType.GPT_4_TURBO):
        super().__init__(model_type=model_type)


    def get_generation(self, context : GenerationContext, options: Options) -> OpenAIGeneration:
        for entry in context.entries:
            if not isinstance(entry, OpenAIEntry):
                raise TypeError(f'Entry {entry} is not of required type OpenAI but {type(entry)}')

        self.log(f'Creating generation request')
        openai_response = self.get_openai_response(context=context, options=options)
        self.log(f"Received generation response. Currently at {self.tokenizer.get_tokens(context=context)} tokens")

        return OpenAIGeneration(generator=openai_response)


    def get_openai_response(self, context : GenerationContext, options: Options) -> Stream[ChatCompletionChunk]:
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
        openai_generator = openai.chat.completions.create(**args_dict)
        return openai_generator


from __future__ import annotations
from typing import Optional
from enum import Enum
import base64
import io

from PIL.Image import Image as PILImage
from PIL import Image
from dataclasses import dataclass
from .flags import Flags
from .speaker import Speaker
from .._serialization import Dillable
# ----------------------------------------------

class APIType(Enum):
    OPENAI = 'OPENAI'
    GOOGLE = 'GOOGLE'
    ANTHROPIC = 'ANTHROPIC'


@dataclass
class Entry(Dillable):
    speaker : Speaker
    msg : str
    image : Optional[PILImage] = None
    flags : Optional[Flags] = None

    def add_msg(self, msg : str):
        self.msg += msg

    def join(self, entry : Entry):
        self.msg += entry.msg
        new_img = entry.get_image()
        if new_img:
            self.image = new_img

    # ----------------------------------------------------
    # get

    def as_dict(self, api_type : APIType) -> dict:
        if api_type == APIType.OPENAI:
            return self.get_openai_data()
        else:
            raise ValueError(f'API type {api_type} not supported')

    def get_msg(self) -> str:
        return self.msg

    def get_role(self) -> str:
        return self.speaker.role.value

    def get_name(self) -> str:
        return self.speaker.name

    def get_image(self) -> Optional[PILImage]:
        return self.image

    def print(self):
        print(self)

    def __str__(self):
        speaker_msg = f'\n{self.get_name()}({self.get_role()})'
        as_str = speaker_msg + f':{self.get_msg()}'
        return as_str


    # ----------------------------------------------------
    # get

    def get_openai_data(self) -> dict:
        data = {'name': self.speaker.name if self.speaker.name else 'unnamed',
                'role': self.speaker.role.value}

        if not self.image:
            content = self.msg
        else:
            img_bytes = self.get_bytes(image=self.image)
            base64_image = self.get_base64(byte_content=img_bytes)
            text = {
                "type": "text",
                "text": f"{self.msg}"
            }
            image = {
                "type": "image_url",
                "image_url": {"url": f"data:image/JPEG;base64,{base64_image}"}
            }
            content = [text, image]

        data['content'] = content
        return data


    @staticmethod
    def get_base64(byte_content : bytes):
        base64_content = base64.b64encode(byte_content).decode('utf-8')
        return base64_content


    @staticmethod
    def get_bytes(image) -> bytes:
        if image.mode in ('LA', 'RGBA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image = image.convert('RGB') if image.mode == 'RGBA' else image.convert('L').convert('RGB')
            background.paste(rgb_image, mask=image.split()[-1])
            image = background

        image.show()
        buffer = io.BytesIO()
        image.save(buffer, format=f'JPEG')
        img_bytes = buffer.getvalue()
        return img_bytes

    # ----------------------------------------------------
    # convenience methdos

    @classmethod
    def get_user(cls, msg : str, name : str = '') -> Entry:
        return cls(speaker=Speaker.get_user(name=name), msg=msg)

    @classmethod
    def get_system(cls, msg : str) -> Entry:
        return cls(speaker=Speaker.get_system(name='SYSTEM'), msg=msg)

    @classmethod
    def get_agent(cls, msg : str, name : str = '') -> Entry:
        return cls(speaker=Speaker.get_agent(name=name), msg=msg)

    @classmethod
    def tool(cls, msg : str, name : str) -> Entry:
        return cls(speaker=Speaker.get_tool(name=name), msg=msg)

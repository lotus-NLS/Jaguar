from __future__ import annotations
from typing import Optional
from enum import Enum

from PIL.Image import Image as PILImage
from hollarek.templates import Dillable
from hollarek.file import ImageConverter, ImageFormat
from dataclasses import dataclass
from .flags import Flags
from .speaker import Speaker, Role
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

    def __iadd__(self, other : Entry) -> Entry:
        if not isinstance(other, Entry):
            raise ValueError(f'Entry can only be added to another Entry. Got {type(other)}')

        self.msg += other.msg
        new_img = other.get_image()
        if new_img:
            self.image = new_img
        return self

    # ----------------------------------------------------
    # get

    def as_dict(self, api_type : APIType, with_vision : bool = True) -> dict:
        if api_type == APIType.OPENAI:
            return self.get_openai_data(with_vision=with_vision)
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

    def get_openai_data(self, with_vision : bool) -> dict:
        data = {'role': self.speaker.role.value}
        if self.speaker.role == Role.TOOL:
            data['name'] = self.speaker.name if self.speaker.name else 'unnamed'

        if not self.image or not with_vision:
            content = self.msg
        else:
            img_fmt = self.image.format
            image = self.image
            if image.mode != 'RGB':
                image = ImageConverter.to_rgb(image=image)
            base64_image = ImageConverter.as_base64_str(image, img_format=img_fmt)
            text = {
                "type": "text",
                "text": f"{self.msg}"
            }
            image = {
                "type": "image_url",
                "image_url": {"url": f"data:image/{img_fmt};base64,{base64_image}"}
            }
            content = [text, image]

        data['content'] = content
        return data

    # ----------------------------------------------------
    # convenience methods

    @classmethod
    def as_user(cls, msg: str, name: str = '', image: Optional[PILImage] = None) -> 'Entry':
        return cls(speaker=Speaker.get_user(name=name), msg=msg, image=image)

    @classmethod
    def as_system(cls, msg: str, image: Optional[PILImage] = None) -> 'Entry':
        return cls(speaker=Speaker.get_system(name='SYSTEM'), msg=msg, image=image)

    @classmethod
    def as_agent(cls, msg: str, name: str = '', image: Optional[PILImage] = None) -> 'Entry':
        return cls(speaker=Speaker.get_agent(name=name), msg=msg, image=image)

    @classmethod
    def as_tool(cls, msg: str, name: str, image: Optional[PILImage] = None) -> 'Entry':
        return cls(speaker=Speaker.get_tool(name=name), msg=msg, image=image)
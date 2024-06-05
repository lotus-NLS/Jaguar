from __future__ import annotations
from typing import Optional
from enum import Enum

from PIL.Image import Image as PILImage
from holytools.file import ImageConverter, ImageSerializer
from dataclasses import dataclass

# ----------------------------------------------


@dataclass
class Entry:
    msg : str
    role: Role
    name : Optional[str] = None
    image: Optional[PILImage] = None


    def __post_init__(self):
        if not self.name and self.role == Role.TOOL:
            raise ValueError('Tool must have a name')

    def __iadd__(self, other : Entry) -> Entry:
        if not isinstance(other, Entry):
            raise ValueError(f'Entry can only be added to another Entry. Got {type(other)}')

        self.msg += other.msg
        new_img = other.image
        if new_img:
            self.image = new_img
        return self

    def add_msg(self, msg : str):
        self.msg += msg

    @classmethod
    def as_user(cls, msg: str, name: Optional[str] = None, image: Optional[PILImage] = None) -> 'Entry':
        return cls(role=Role.USER, name=name, msg=msg, image=image)

    @classmethod
    def as_system(cls, msg: str, image: Optional[PILImage] = None) -> 'Entry':
        return cls(role=Role.SYSTEM, name=None, msg=msg, image=image)

    @classmethod
    def as_agent(cls, msg: str, name: Optional[str] = None, image: Optional[PILImage] = None) -> 'Entry':
        return cls(role=Role.AGENT, name=name, msg=msg, image=image)

    @classmethod
    def as_tool(cls, msg: str, name: str, image: Optional[PILImage] = None) -> 'Entry':
        return cls(role=Role.TOOL, name=name, msg=msg, image=image)

    # ----------------------------------------------------
    # view

    def as_dict(self, api_type: APIType, with_vision: bool = True) -> dict:
        if api_type == APIType.OPENAI:
            return self.as_openai_dict(with_vision=with_vision)
        else:
            raise ValueError(f'API type {api_type} not supported')

    def get_image_as_base64(self) -> Optional[str]:
        img_fmt = self.image.format
        image = self.image
        if image.mode != 'RGB':
            image = ImageConverter.to_rgb(image=image)
        base64_image = ImageSerializer.as_base64_str(image, img_format=img_fmt)
        return base64_image

    def as_str(self):
        name_str = f'Unnamed' if not self.name else self.name
        as_str = f'{self.role.value}({name_str}): {self.msg}'
        if self.image:
            as_str += f'\n{self.get_image_as_base64()}'
        return as_str

    def __str__(self):
        return self.as_str()

    # ----------------------------------------------------
    # get

    def as_openai_dict(self, with_vision : bool) -> dict:
        data = {'role': self.role.value}
        if self.role == Role.TOOL:
            data['name'] = self.name if self.name else 'unnamed'

        if not self.image or not with_vision:
            content = self.msg
        else:
            img_fmt = self.image.format
            base64_image = self.get_image_as_base64()
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

class APIType(Enum):
    OPENAI = 'OPENAI'
    GOOGLE = 'GOOGLE'
    ANTHROPIC = 'ANTHROPIC'

class Role(Enum):
    TOOL = 'function'
    USER = 'user'
    AGENT = 'assistant'
    SYSTEM = 'system'

    def __str__(self):
        return self.value

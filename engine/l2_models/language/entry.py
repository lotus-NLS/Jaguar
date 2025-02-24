from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from PIL.Image import Image as PILImage

from engine.l3_aos.tools import ToolOutput
from engine.l3_aos.workspaces import Workspace
from holytools.abstract import JsonDataclass
from holytools.fileIO.converters import ImageConverter
from holytools.userIO import MessageFormatter


# ----------------------------------------------

@dataclass
class Entry(JsonDataclass):
    msg : str
    role: Role
    name : Optional[str] = None
    image: Optional[PILImage] = None

    def __post_init__(self):
        if not self.name and self.role == Role.TOOL:
            raise ValueError('Tool must have a name')

    @classmethod
    def from_workspace(cls, ws : Workspace):
        msg = f'{ws.get_desc()}\n'
        msg += MessageFormatter.get_boxed(text=ws.get_text(), headline=ws.get_name())
        return Entry.tool(name=ws.get_name(), msg=msg, image=ws.get_image())

    @classmethod
    def from_tool_output(cls, tool_output : ToolOutput) -> Entry:
        return Entry.tool(msg=tool_output.get_report(), name=tool_output.tool_name)

    @classmethod
    def user(cls, msg: str, name: Optional[str] = None, image: Optional[PILImage] = None) -> Entry:
        return cls(role=Role.USER, name=name, msg=msg, image=image)

    @classmethod
    def system(cls, msg: str, image: Optional[PILImage] = None) -> Entry:
        return cls(role=Role.SYSTEM, name=None, msg=msg, image=image)

    @classmethod
    def agent(cls, msg: str, name: Optional[str] = None, image: Optional[PILImage] = None) -> Entry:
        return cls(role=Role.AGENT, name=name, msg=msg, image=image)

    @classmethod
    def tool(cls, msg: str, name: str, image: Optional[PILImage] = None) -> Entry:
        return cls(role=Role.TOOL, name=name, msg=msg, image=image)

    def __eq__(self, other):
        if not isinstance(other, Entry):
            return False
        return self.msg == other.msg and self.role == other.role and self.name == other.name and self.image == other.image

    def add(self, msg : str, at_start : bool = False):
        first = self.msg if not at_start else msg
        second = msg if not at_start else self.msg
        self.msg = f'{first}\n{second}'

     # ----------------------------------------------------
    # get

    def as_dict(self, api_type: APIType) -> dict:
        if api_type == APIType.OPENAI:
            return self.as_openai_dict()
        else:
            raise ValueError(f'API type {api_type} not supported')

    def get_view(self) -> str:
        name_str = f'({self.name})' if not self.name is None else ''
        return f'{self.role.value}{name_str}: {self.msg}'

    def as_openai_dict(self) -> dict:
        data = {'role': self.role.value}
        if self.role == Role.TOOL:
            data['name'] = self.name if self.name else 'unnamed'

        if not self.image:
            content = self.msg
        else:
            text = {
                "type": "text",
                "text": f"{self.msg}"
            }
            image = {
                "type": "image_url",
                "image_url": {"url": f"data:image/{self.image.format};base64,{self.get_image_as_base64()}"}
            }
            content = [text, image]

        data['content'] = content
        return data

    def get_image_as_base64(self) -> Optional[str]:
        image = self.image
        if image.mode != 'RGB':
            image = ImageConverter.to_rgb(img=image)
        base64_image = ImageConverter.to_base64_str(image)
        return base64_image



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


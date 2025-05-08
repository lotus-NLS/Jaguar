from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from PIL.Image import Image as PILImage

from engine.l3_aos.tools import ToolReport
from engine.l3_aos.workspaces import Workspace
from holytools.abstract import JsonDataclass
from holytools.fileIO.converters import ImageConverter
from holytools.userIO import MessageFormatter


# ----------------------------------------------

@dataclass
class Message(JsonDataclass):
    text : str
    role: Role
    name : Optional[str] = None
    image: Optional[PILImage] = None

    def __post_init__(self):
        if not self.name and self.role == Role.TOOL:
            raise ValueError('Tool must have a name')
        if self.image:
            if self.image.mode != 'RGB':
                self.image = ImageConverter.to_rgb(img=self.image)

    @classmethod
    def from_workspace(cls, ws : Workspace, active : bool = True) -> Message:
        msg = f'{ws.get_desc()}\n'
        if active:
            headline = f'{ws.get_name()}[Active]'

        else:
            headline = f'{ws.get_name()}[Archived]'
        msg += MessageFormatter.get_boxed(text=ws.get_text(), headline=headline)
        return Message.tool(name=ws.get_name(), msg=msg, image=ws.get_image())

    @classmethod
    def from_tool_output(cls, tool_output : ToolReport) -> Message:
        return Message.tool(msg=tool_output.get_report(), name=tool_output.tool_name)

    @classmethod
    def user(cls, msg: str, name: Optional[str] = None, image: Optional[PILImage] = None) -> Message:
        return cls(role=Role.USER, name=name, text=msg, image=image)

    @classmethod
    def system(cls, msg: str, image: Optional[PILImage] = None) -> Message:
        return cls(role=Role.SYSTEM, name=None, text=msg, image=image)

    @classmethod
    def agent(
            cls, msg: str, name: Optional[str] = None, image: Optional[PILImage] = None) -> Message:
        return cls(role=Role.AGENT, name=name, text=msg, image=image)

    @classmethod
    def tool(cls, msg: str, name: str, image: Optional[PILImage] = None) -> Message:
        return cls(role=Role.TOOL, name=name, text=msg, image=image)

    def __eq__(self, other):
        if not isinstance(other, Message):
            return False
        return self.text == other.text and self.role == other.role and self.name == other.name and self.image == other.image

    def add(self, msg : str, at_start : bool = False):
        first = self.text if not at_start else msg
        second = msg if not at_start else self.text
        self.text = f'{first}\n{second}'

     # ----------------------------------------------------
    # get

    def get_view(self) -> str:
        name_str = f'({self.name})' if not self.name is None else ''
        return f'{self.role.value}{name_str}: {self.text}'

    def as_openai_dict(self) -> dict:
        data = {'role': self.role.value}
        if self.role == Role.TOOL:
            data['name'] = self.name if self.name else 'unnamed'

        if not self.image:
            content = self.text
        else:
            b64_img = ImageConverter.to_base64_str(image=self.image)
            image_url = {"url": f"data:image/{self.image.format};base64,{b64_img}"}

            text = {"type": "text", "text": f"{self.text}"}
            image = {"type": "image_url", "image_url": image_url}
            content = [text, image]

        data['content'] = content
        return data


class Role(Enum):
    TOOL = 'function'
    USER = 'user'
    AGENT = 'assistant'
    SYSTEM = 'system'


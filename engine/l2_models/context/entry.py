from __future__ import annotations
from typing import Optional
from enum import Enum

from PIL.Image import Image as PILImage
from pkg_resources import working_set

from engine.l3_aos.tools import ToolOutput
from engine.l3_aos.workspace import Workspace
from holytools.abstract import JsonDataclass
from holytools.fileIO.converters import ImageConverter
from dataclasses import dataclass

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
    def from_workspace(cls, workspace : Workspace):
        msg = f'{workspace.get_desc()}\n'
        msg += cls.get_boxed(text=workspace.get_text(), headline=workspace.get_name())
        return Entry.tool(name=workspace.get_name(), msg=msg, image=workspace.get_image())

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


    @staticmethod
    def get_boxed(text: str, headline: str = "") -> str:
        lines = text.split("\n")
        max_length = max(max(len(line) for line in lines), len(headline))
        border = "+" + "-" * (max_length + 2) + "+"
        headline = f' {headline} '
        headline_line = f"+{headline.center(max_length + 2, '-')}+" if headline else border
        boxed_text = [headline_line] + [f"| {line.ljust(max_length)} |" for line in lines] + [border]
        return "\n".join(boxed_text)


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


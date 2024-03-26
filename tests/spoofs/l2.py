from typing import Optional
from PIL.Image import Image as PILImage
from engine.l2_os import Workspace
from enum import Enum
# ---------------------------------------------------------

class Plant:
    def __init__(self):
        self.is_watered : bool = False

class MockChoice(Enum):
    choiceOne = 'choiceOne'
    choiceTwo = 'choiceTwo'


class MockWorkspace(Workspace):
    def __init__(self):
        super().__init__()
        self.text_content = 'Initial'

    def open(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    def get_text(self) -> str:
        return self.text_content

    def get_image(self) -> Optional[PILImage]:
        return None

    def add(self, msg: str):
        self.text_content += ' ' + msg

    def reset(self):
        self.text_content = ''

    def get_desc(self) -> str:
        return ''


class InvalidArgWorkspace(Workspace):
    def get_text(self) -> str:
        return ''

    def get_image(self) -> Optional[PILImage]:
        return None

    def invalid_type_func(self, plant : Plant):
        pass

    def get_desc(self) -> str:
        return ''

    def open(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass


class EnumArgWorkspace(Workspace):
    def get_text(self) -> str:
        return ''

    def get_image(self) -> Optional[PILImage]:
        return None

    @staticmethod
    def decide(choice : MockChoice):
        print(f'I decided on {choice}')

    def get_desc(self) -> str:
        return ''

    def open(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

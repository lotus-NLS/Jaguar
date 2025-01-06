from typing import Optional

from PIL.Image import Image as PILImage

from engine.l3_os import Workspace


class Plant:
    def __init__(self):
        self.is_watered : bool = False


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

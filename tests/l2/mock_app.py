from typing import Optional
from PIL.Image import Image as PILImage
from engine.l2_os import Tab
# ---------------------------------------------------------

class MockTab(Tab):
    def __init__(self, uri: str):
        super().__init__(uri)
        self.text_content = 'Initial'

    def get_text(self) -> str:
        return self.text_content

    def get_image(self) -> Optional[PILImage]:
        return None

    def add(self, msg: str):
        self.text_content += ' ' + msg

    def reset(self):
        self.text_content = ''
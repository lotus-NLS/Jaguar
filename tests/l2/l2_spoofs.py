from typing import Optional

from PIL.Image import Image as PILImage
from holytools.fileIO import ImageFile, FileMock
from api import Entry
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


class SpoofEntries:
    def __init__(self):
        self.introduction_request = Entry.user(
            msg='Hi there, pleased to meet you! Who are you and what is your expertise?')
        self.repetition_request = Entry.user(msg='Can you please repeat what I said above in its entirety?')

        fpath = FileMock.lend_png().fpath  # Assuming SpoofFiles and ImageIO are defined elsewhere
        img_io = ImageFile(fpath=fpath)
        img_content = img_io.read()
        self.image_entry = Entry.user(msg='Can you describe what\'s in this image?', image=img_content)

        self.welcome_request = Entry.user(msg='## Automated message: Please greet our eight guests and welcome them to our home! You need only do this once, every guest will see it.')
        self.chef_notification_request = Entry.user(msg='Also please notify the chef that we need food for eight people.')
        self.write_text_entries_request = Entry.user(msg='Please tell me how many guests there are without invoking the display, then display a (single) warm welcome message')
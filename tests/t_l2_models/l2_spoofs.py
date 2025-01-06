from typing import Optional



from engine.l3_aos import Workspace
from holytools.fileIO import ImageFile, FileMock
from api import Entry




class MockEntries:
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
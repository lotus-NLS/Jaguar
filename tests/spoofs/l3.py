from engine.l4_tools import Tool, ToolArg
from holytools.fileIO import ImageFile, FileMock
from api import Entry

# ---------------------------------------------------------

class Greet(Tool):
    def __init__(self, call_timeout: float = 1):
        super().__init__(call_timeout=call_timeout)
        self.text_arg : ToolArg = ToolArg(name="text",
                                          desc='This is the text that will be displayed to the guests on the monitor.'
                                               'There is only one monitor so you need only call this once')

    def do(self):
        print(self.text_arg.input)

    def get_desc(self) -> str:
        return "This tool is connected with a monitor in our house and allows you to send a message to our guests"


class NotifyChef(Tool):
    def __init__(self, call_timeout: float = 1):
        super().__init__(call_timeout=call_timeout)
        self.number_of_guests_arg : ToolArg = ToolArg(name="number_of_guests")

    def do(self):
        print(f'We need to prepare food for {self.number_of_guests_arg.input} guests')

    def get_desc(self) -> str:
        return "This tool will notify the chec of the number of guests that we need to prepare food for"


class SpoofEntries:
    def __init__(self):
        self.introduction_request = Entry.as_user(
            msg='Hi there, pleased to meet you! Who are you and what is your expertise?')
        self.repetition_request = Entry.as_user(msg='Can you please repeat what I said above in its entirety?')

        fpath = FileMock.lend_png().fpath  # Assuming SpoofFiles and ImageIO are defined elsewhere
        img_io = ImageFile(fpath=fpath)
        img_content = img_io.read()
        self.image_entry = Entry.as_user(msg='Can you describe what\'s in this image?', image=img_content)

        self.welcome_request = Entry.as_user(msg='## Automated message: Please greet our eight guests and welcome them to our home! You need only do this once, every guest will see it.')
        self.chef_notification_request = Entry.as_user(msg='Also please notify the chef that we need food for eight people.')
        self.write_text_entries_request = Entry.as_user(msg='Please tell me how many guests there are without invoking the display, then display a (single) warm welcome message')


class SpoofToolDocs:
    def __init__(self):
        self.application_name = 'display'
        self.greet_tool_docs = Greet().get_doc()
        self.notify_chef_docs = NotifyChef().get_doc()
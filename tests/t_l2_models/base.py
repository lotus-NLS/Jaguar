import time
from typing import Optional

from api import Entry
from engine.l3_aos.tools import Tool, ToolArg
from holytools.fileIO import ImageFile, FileMock

from engine.l2_models import Options, OpenAIModel, Context, Generation
from engine.l3_aos.tools import ToolCallMap
from tests.credtest import CredTest

# --------------------------------------------------------------------------------


class OpenAITest(CredTest):
    def setUp(self):
        self.example_entries = ExampleEntries()
        self.greet_tool = Greet()
        self.noify_chef_tool = NotifyChef()

        self.text_only = Options.text_only()
        self.tool_allowed = Options()

        self.default_model = OpenAIModel.default_model(api_key=self.openai_apikey)
        self.textbox = TextBox()

    def get_action(self, context : Context, generation : Generation) -> (str, ToolCallMap):
        prompts_context = [entry.msg for entry in context.entries]
        call_map : ToolCallMap = ToolCallMap()

        print(f'-> Prompts: \n {prompts_context}')
        print("->Generated Text Content:")
        for chunk in generation:
            self.textbox.add(chunk.get_text())
            call_map.add(chunk.get_call_map())
        print()

        if call_map:
            call_map.print_info()
        time.sleep(0.1)

        return self.textbox.total_text, call_map

class TextBox:
    def __init__(self, logger : callable = print):
        self.line : str = ''
        self.max_len : int = 100
        self.logger = logger
        self.total_text = ''

    def add(self, msg : Optional[str] = None):
        if msg is None:
            return

        self.line += msg
        self.total_text += msg
        if len(self.line) > self.max_len:
            msg = f'{msg}\n'
            self.line = ''
        print(msg, end='')

    def reset(self):
        self.line = ''


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

class ExampleEntries:
    def __init__(self):
        self.introduction = Entry.user(msg='Hi there, pleased to meet you! Who are you and what is your expertise?')
        self.repetition = Entry.user(msg='Can you please repeat what I said above in its entirety?')

        fpath = FileMock.lend_png().fpath
        img_io = ImageFile(fpath=fpath)
        img_content = img_io.read()
        self.image_entry = Entry.user(msg='Can you describe what\'s in this image?', image=img_content)

        self.welcome_request = Entry.user(msg='## Automated message: Please greet our eight guests and welcome them to our home! You need only do this once, every guest will see it.')
        self.notify_chef = Entry.user(msg='Also please notify the chef that we need food for eight people.')
        self.write_num_guests = Entry.user(msg='Please tell me how many guests there are without invoking the display, then display a (single) warm welcome message')

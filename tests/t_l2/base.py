import time
from typing import Optional

from engine.l2_models import Options, OpenAIModel, Generation
from engine.l2_models.context import Entry, Context
from engine.l3_aos.tools import Tool, ToolArg, ToolCall, ToolDoc
from holytools.fileIO import ImageFile, ExampleFiles
from tests.credtest import CredentialDependentTest


# --------------------------------------------------------------------------------


class OpenAITest(CredentialDependentTest):
    def setUp(self):
        self.example_entries = ExampleEntries()
        self.greet_tool = Greet()
        self.noify_chef_tool = NotifyChef()

        self.text_only = Options.text_only()
        self.tool_allowed = Options()

        self.default_model : OpenAIModel = OpenAIModel.default_model(api_key=self.openai_apikey)
        self.textbox = TextBox()

    def get_results(self, entries : list[Entry], docs : list[ToolDoc], options : Options) -> tuple[str, list[ToolCall]]:
        context = Context(entries=entries, docs=docs)
        generation = self.default_model.get_generation(context=context, options=options)
        prompts_context = [entry.msg for entry in context.entries]

        print(f'-> Prompts: \n {prompts_context}')
        print("->Generated Text Content:")
        for chunk in generation:
            self.textbox.add(chunk.get_text())
        self.print_action_info(generation)
        time.sleep(0.1)
        return generation.get_text(), generation.get_tool_calls()

    @staticmethod
    def print_action_info(generation : Generation):
        print(f'\n-> Generated tool calls')
        for call in generation.get_tool_calls():
            print(f'tool name: {call.name}')
            print(call.get_args_dict())

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

    def get_args(self) -> list[ToolArg]:
        return [self.text_arg]

class NotifyChef(Tool):
    def __init__(self, call_timeout: float = 1):
        super().__init__(call_timeout=call_timeout)
        self.number_of_guests_arg : ToolArg = ToolArg(name="number_of_guests")

    def do(self):
        print(f'We need to prepare food for {self.number_of_guests_arg.input} guests')

    def get_desc(self) -> str:
        return "This tool will notify the chec of the number of guests that we need to prepare food for"

    def get_args(self) -> list[ToolArg]:
        return [self.number_of_guests_arg]

class ExampleEntries:
    def __init__(self):
        self.introduction = Entry.user(msg='Hi there, pleased to meet you! Who are you and what is your expertise?')
        self.repetition = Entry.user(msg='Can you please repeat what I said above in its entirety?')

        fpath = ExampleFiles.lend_png().fpath
        img_io = ImageFile(fpath=fpath)
        img_content = img_io.read()
        self.image_entry = Entry.user(msg='Can you describe what\'s in this image?', image=img_content)

        self.welcome_request = Entry.user(msg='## Automated message: Please greet our eight guests and welcome them to our home! You need only do this once, every guest will see it.')
        self.notify_chef = Entry.user(msg='Also please notify the chef that we need food for eight people.')
        self.write_num_guests = Entry.user(msg='Please tell me how many guests there are without invoking the display, then display a (single) warm welcome message')

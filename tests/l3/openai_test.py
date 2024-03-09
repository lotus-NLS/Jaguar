import time
from typing import Optional

from hollarek.devtools import Unittest
from engine.l3_models import Options, OpenAIModel, Context, Generation, OpenAIModelType
from engine.l4_tools import CallMap
from tests.spoofs import SpoofEntries, SpoofToolDocs

# ---------------------------------------------------------


class LinePrinter:
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


class OpenAITest(Unittest):
    text_options = Options(max_tokens=10)
    default_options = Options()
    default_model = OpenAIModel()
    vision_model = OpenAIModel(OpenAIModelType.GPT_4V)
    lineprinter = LinePrinter()

    @classmethod
    def setUpClass(cls):
        cls.entry_spoofs = SpoofEntries()
        cls.doc_spoof = SpoofToolDocs()

    def tearDown(self):
        self.lineprinter.reset()

    def get_result(self, context : Context, generation : Generation) -> (str, CallMap):
        prompts_context = [entry.get_msg() for entry in context.entries]
        call_map : CallMap = CallMap()

        print(f'-> Prompts: \n {prompts_context}')
        print("->Generated Text Content:")
        for chunk in generation:
            self.lineprinter.add(chunk.get_text())
            call_map.add(chunk.get_call_map())
        print()

        if call_map:
            call_map.print_info()
        time.sleep(0.1)

        return self.lineprinter.total_text, call_map
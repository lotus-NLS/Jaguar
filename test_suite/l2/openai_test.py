import time

from hollarek.devtools import Unittest
from typing import Optional

from engine.l2_models import Options, OpenAIModel, GenerationContext, Generation
from engine.l3_applications import CallMap



class LinePrinter:
    def __init__(self, logger : callable = print):
        self.line : str = ''
        self.max_len : int = 100
        self.logger = logger

    def add(self, msg : Optional[str] = None):
        if msg is None:
            return

        self.line += msg
        if len(self.line) > self.max_len:
            msg = f'{msg}\n'
            self.line = ''
        print(msg, end='')

    def reset(self):
        self.line = ''


class OpenAITest(Unittest):
    default_options = Options()
    model = OpenAIModel()
    lineprinter = LinePrinter()

    def tearDown(self):
        self.lineprinter.reset()

    def log_result(self, context : GenerationContext, generation : Generation):
        prompts_context = [entry.get_content() for entry in context.entries]
        print(f'-> Prompts: \n {prompts_context}')
        print("->Generated Text Content:")
        call_map : CallMap = CallMap()
        for chunk in generation:
            self.lineprinter.add(chunk.get_text())
            call_map.add(chunk.get_call_map())

        print()
        time.sleep(0.1)
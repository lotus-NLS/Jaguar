import time

from devtools import debug
from hollarek.devtools import Unittest
from typing import Optional

from engine.l2_models import Options, OpenAIModel, GenerationContext, Generation
from engine.l3_applications import ToolCall



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
        call_map : dict[int, ToolCall] = {}
        for chunk in generation:
            self.lineprinter.add(chunk.get_text())
            chunk_call_map = chunk.get_call_map()
            for index, call in chunk_call_map.items():
                if not index in call_map:
                    call_map[index] = call
                else:
                    call_map[index].update(partial_call=call)

        print(f'\n-> Generated tool calls')
        for call in list(call_map.values()):
            print(f'tool name: {call.name}')
            debug(call.get_args_dict())

        print()
        time.sleep(0.1)
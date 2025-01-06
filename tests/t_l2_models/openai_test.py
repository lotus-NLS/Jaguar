from __future__ import annotations

import time
from typing import Optional

from engine.l2_models import Options, OpenAIModel, Context, Generation
from engine.l3_aos.tools import ToolCallMap
from tests.credtest import CredTest
from tests.t_l2_models.l2_spoofs import MockEntries


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


class OpenAITest(CredTest):
    def setUp(self):
        self.mock_entries = MockEntries()
        self.default_options = Options()
        self.default_model = OpenAIModel(name='gpt-4', api_key=self.openai_apikey)
        self.lineprinter = LinePrinter()

    def get_result(self, context : Context, generation : Generation) -> (str, ToolCallMap):
        prompts_context = [entry.msg for entry in context.entries]
        call_map : ToolCallMap = ToolCallMap()

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


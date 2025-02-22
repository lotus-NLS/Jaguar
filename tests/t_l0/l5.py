from __future__ import annotations
import string
import random

from engine.l1_agents import Agent
from engine.l2_models import InfOptions
from engine.l2_models.generation.step import TextPipe


class MockPipe(TextPipe):
    def __init__(self, str_len: int = 10, msg_count: int = 5):
        super().__init__()
        self.length = str_len
        self.count = msg_count
        self.current = 0

    def get(self, *args, **kwargs) -> str:
        if self.current < self.count:
            self.current += 1
            msg = ''.join(random.choices(string.ascii_lowercase, k=self.length))
            self.put(msg)
        else:
            self.stop()
        return super().get(*args, **kwargs)


class MockEntity(Agent):
    def handle(self, inf_options : InfOptions = InfOptions()) -> TextPipe:
        _, __ = self, inf_options
        return MockPipe()


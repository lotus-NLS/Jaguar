from __future__ import annotations
import string
import random

from engine.l5_singletons.io.types import Response, Pipe, Task
from engine.l5_singletons.io.engine_io import Handler


class MockTextStream(Pipe):
    def __init__(self, str_len: int = 10, msg_count: int = 5):
        self.length = str_len
        self.count = msg_count
        self.current = 0

    def __iter__(self) -> MockTextStream:
        return self

    def __next__(self) -> str:
        if self.current < self.count:
            self.current += 1
            return ''.join(random.choices(string.ascii_lowercase, k=self.length))
        raise StopIteration


class MockEntity(Handler):
    def handle(self, task: Task) -> Response:
        return Response(user_query=None, primary_stream=MockTextStream())


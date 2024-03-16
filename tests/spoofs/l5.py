from __future__ import annotations
import string
import random

from api.communication.messages import Pipe, Response, Task
from engine.l5_singletons.io.engine_io import Handler


class MockPipe(Pipe):
    def __init__(self, str_len: int = 10, msg_count: int = 5):
        super().__init__()
        self.length = str_len
        self.count = msg_count
        self.current = 0

    def get(self) -> str:
        if self.current < self.count:
            self.current += 1
            msg = ''.join(random.choices(string.ascii_lowercase, k=self.length))
            self.put(msg)
        else:
            self.stop()
        return super().get()


class MockEntity(Handler):
    def handle(self, task: Task) -> Response:
        return Response(text_queue=MockPipe())


from __future__ import annotations
import string
import random

from api import Entry, Speaker, Role
from hollarek.devtools import Unittest
from engine.l5_singletons.io.engine_io import EngineIO, Entity
from engine.l5_singletons.io.types import ServerResponse, TextStream, Task
# --------------------------------------------

class MockTextStream(TextStream):
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


class MockEntity(Entity):
    def handle(self, entry: Entry) -> ServerResponse:
        return ServerResponse(user_query=None, text_stream=MockTextStream())


class TestEngineIO(Unittest):
    @classmethod
    def setUpClass(cls):
        pass


    def setUp(self):
        EngineIO.reset_instance()
        self.entity = MockEntity()
        self.app = EngineIO(entity=self.entity)


    def test_initialization(self):
        self.assertIsNotNone(self.app)

    def test_response_stream(self):
        msg = 'Hello, do something'
        print(f'User said: {msg}')
        entry = Entry(msg=msg, speaker=Speaker(role=Role.USER))
        task = Task(new_entries=[entry])
        response = self.app.handle(task)

        self.assertIsInstance(response, ServerResponse)
        self.assertIsInstance(response.text_stream, TextStream)

        print(f'Engine responded: With following text stream')
        for text in response.text_stream:
            print(text)


if __name__ == '__main__':
    TestEngineIO.execute_all()

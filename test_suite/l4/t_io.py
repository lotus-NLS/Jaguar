from __future__ import annotations
import string
import random

from api import Entry, Speaker, Role
from hollarek.dev import Unittest
from engine.l4_singletons.io.engine_io import EngineIO, Entity
from engine.l4_singletons.io.types import ServerResponse, TextStream, UserQuery
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


class MockQuery(UserQuery):
    msg: str

    def get_query_display(self) -> str:
        return f'{self.msg} (y/n)'


class MockServer(Entity):
    def get_response(self, entry: Entry) -> ServerResponse:
        return ServerResponse(user_query=None, text_stream=MockTextStream())


class TestEngineIO(Unittest):
    def setUp(self):
        self.server = MockServer()
        self.app = EngineIO(self.server)

    @classmethod
    def setUpClass(cls):
        pass

    def test_initialization(self):
        self.assertIsNotNone(self.app)

    def test_response_stream(self):
        entry = Entry(msg='Hello, do something', speaker=Speaker(role=Role.USER))
        response = self.app.get_response_stream(entry)

        self.assertIsInstance(response, ServerResponse)
        self.assertIsInstance(response.user_query, MockQuery)
        self.assertIsInstance(response.text_stream, MockTextStream)

        for text in response.text_stream:
            print(text)


if __name__ == '__main__':
    TestEngineIO.execute_all()

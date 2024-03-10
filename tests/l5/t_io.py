from __future__ import annotations

from api import Entry, Speaker, Role
from hollarek.devtools import Unittest
from tests.spoofs import MockEntity

from engine.l5_singletons.io.engine_io import EngineIO
from engine.l5_singletons.io.types import Response, Pipe, Task
# --------------------------------------------



class TestEngineIO(Unittest):
    @classmethod
    def setUpClass(cls):
        pass


    def setUp(self):
        EngineIO.reset_instance()
        self.entity = MockEntity()
        self.io = EngineIO(handler=self.entity)


    def test_initialization(self):
        self.assertIsNotNone(self.io)

    def test_response_stream(self):
        msg = 'Hello, do something'
        print(f'User said: {msg}')
        entry = Entry(msg=msg, speaker=Speaker(role=Role.USER))
        task = Task(new_entries=[entry])
        response = self.io.handle(task)

        self.assertIsInstance(response, Response)
        self.assertIsInstance(response.primary_stream, Pipe)

        print(f'Engine responded: With following text stream')
        for text in response.primary_stream:
            print(text)


if __name__ == '__main__':
    TestEngineIO.execute_all()

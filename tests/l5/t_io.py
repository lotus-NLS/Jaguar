from __future__ import annotations

from api import Entry, Speaker, Role
from hollarek.devtools import Unittest
from tests.spoofs import MockEntity

from engine.l5_singletons.io.engine_io import IO
from engine.l5_singletons import Pipe, Task


# --------------------------------------------

class TestEngineIO(Unittest):
    @classmethod
    def setUpClass(cls):
        pass


    def setUp(self):
        IO.reset_instance()
        self.entity = MockEntity()
        self.io = IO(handler=self.entity)


    def test_initialization(self):
        self.assertIsNotNone(self.io)

    # def test_response_stream(self):
    #     msg = 'Hello, do something'
    #     print(f'User said: {msg}')
    #     entry = Entry(msg=msg, speaker=Speaker(role=Role.USER))
    #     task = Task(new_entries=[entry])
    #     response = self.io.(task)
    #
    #     self.assertIsInstance(response, Pipe)
    #
    #     print(f'Engine responded: With following text stream')

if __name__ == '__main__':
    TestEngineIO.execute_all()
